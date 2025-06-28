from typing import Dict, Any, List, Optional, Union
import re
import logging
from enum import Enum


class NodeType(Enum):
    CONDITION = "condition"
    ACTION = "action"
    MESSAGE = "message"
    WEBHOOK = "webhook"
    HANDOVER = "handover"


class DecisionTreeEngine:
    """Decision tree engine for chatbot workflow automation"""
    
    def __init__(self):
        pass
    
    async def process_decision_tree(
        self,
        tree_config: Dict[str, Any],
        user_message: str,
        conversation_context: Dict[str, Any],
        ai_response: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a decision tree based on user input and context
        
        Returns:
        - action: The action to take (continue, message, webhook, handover)
        - response: Modified or new response message
        - metadata: Additional metadata for the action
        """
        
        if not tree_config or "nodes" not in tree_config:
            return {"action": "continue", "response": ai_response}
        
        try:
            # Start from root node
            root_node_id = tree_config.get("root", "start")
            current_node = self._find_node(tree_config["nodes"], root_node_id)
            
            if not current_node:
                logging.warning(f"Root node '{root_node_id}' not found in decision tree")
                return {"action": "continue", "response": ai_response}
            
            # Process the tree
            result = await self._process_node(
                current_node,
                tree_config["nodes"],
                user_message,
                conversation_context,
                ai_response
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Error processing decision tree: {e}")
            return {"action": "continue", "response": ai_response}
    
    async def _process_node(
        self,
        node: Dict[str, Any],
        all_nodes: List[Dict[str, Any]],
        user_message: str,
        context: Dict[str, Any],
        ai_response: Optional[str]
    ) -> Dict[str, Any]:
        """Process a single node in the decision tree"""
        
        node_type = NodeType(node.get("type", "condition"))
        
        if node_type == NodeType.CONDITION:
            return await self._process_condition_node(node, all_nodes, user_message, context, ai_response)
        elif node_type == NodeType.MESSAGE:
            return await self._process_message_node(node, all_nodes, user_message, context, ai_response)
        elif node_type == NodeType.ACTION:
            return await self._process_action_node(node, all_nodes, user_message, context, ai_response)
        elif node_type == NodeType.WEBHOOK:
            return await self._process_webhook_node(node, all_nodes, user_message, context, ai_response)
        elif node_type == NodeType.HANDOVER:
            return await self._process_handover_node(node, all_nodes, user_message, context, ai_response)
        else:
            return {"action": "continue", "response": ai_response}
    
    async def _process_condition_node(
        self,
        node: Dict[str, Any],
        all_nodes: List[Dict[str, Any]],
        user_message: str,
        context: Dict[str, Any],
        ai_response: Optional[str]
    ) -> Dict[str, Any]:
        """Process a condition node - evaluates conditions and routes to next node"""
        
        conditions = node.get("conditions", [])
        
        for condition in conditions:
            if await self._evaluate_condition(condition, user_message, context, ai_response):
                next_node_id = condition.get("next_node")
                if next_node_id:
                    next_node = self._find_node(all_nodes, next_node_id)
                    if next_node:
                        return await self._process_node(next_node, all_nodes, user_message, context, ai_response)
        
        # No condition matched, use default next node or continue
        default_next = node.get("default_next")
        if default_next:
            next_node = self._find_node(all_nodes, default_next)
            if next_node:
                return await self._process_node(next_node, all_nodes, user_message, context, ai_response)
        
        return {"action": "continue", "response": ai_response}
    
    async def _process_message_node(
        self,
        node: Dict[str, Any],
        all_nodes: List[Dict[str, Any]],
        user_message: str,
        context: Dict[str, Any],
        ai_response: Optional[str]
    ) -> Dict[str, Any]:
        """Process a message node - returns a custom message"""
        
        message_template = node.get("message", "")
        
        # Replace variables in message template
        message = self._replace_variables(message_template, user_message, context)
        
        # Check if we should continue to next node
        next_node_id = node.get("next_node")
        if next_node_id:
            next_node = self._find_node(all_nodes, next_node_id)
            if next_node:
                next_result = await self._process_node(next_node, all_nodes, user_message, context, message)
                return next_result
        
        return {
            "action": "message",
            "response": message,
            "metadata": node.get("metadata", {})
        }
    
    async def _process_action_node(
        self,
        node: Dict[str, Any],
        all_nodes: List[Dict[str, Any]],
        user_message: str,
        context: Dict[str, Any],
        ai_response: Optional[str]
    ) -> Dict[str, Any]:
        """Process an action node - performs specific actions"""
        
        action_type = node.get("action_type", "continue")
        
        return {
            "action": action_type,
            "response": ai_response,
            "metadata": node.get("metadata", {})
        }
    
    async def _process_webhook_node(
        self,
        node: Dict[str, Any],
        all_nodes: List[Dict[str, Any]],
        user_message: str,
        context: Dict[str, Any],
        ai_response: Optional[str]
    ) -> Dict[str, Any]:
        """Process a webhook node - triggers webhook call"""
        
        return {
            "action": "webhook",
            "response": ai_response,
            "metadata": {
                "webhook_url": node.get("webhook_url"),
                "webhook_method": node.get("webhook_method", "POST"),
                "webhook_data": node.get("webhook_data", {}),
                **node.get("metadata", {})
            }
        }
    
    async def _process_handover_node(
        self,
        node: Dict[str, Any],
        all_nodes: List[Dict[str, Any]],
        user_message: str,
        context: Dict[str, Any],
        ai_response: Optional[str]
    ) -> Dict[str, Any]:
        """Process a handover node - transfers to human agent"""
        
        handover_message = node.get("handover_message", "Transferring you to a human agent...")
        
        return {
            "action": "handover",
            "response": handover_message,
            "metadata": {
                "reason": node.get("reason", "User request"),
                "department": node.get("department"),
                **node.get("metadata", {})
            }
        }
    
    async def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        user_message: str,
        context: Dict[str, Any],
        ai_response: Optional[str]
    ) -> bool:
        """Evaluate a single condition"""
        
        condition_type = condition.get("type", "contains")
        
        if condition_type == "contains":
            return await self._evaluate_contains(condition, user_message, context)
        elif condition_type == "regex":
            return await self._evaluate_regex(condition, user_message, context)
        elif condition_type == "intent":
            return await self._evaluate_intent(condition, user_message, context, ai_response)
        elif condition_type == "context":
            return await self._evaluate_context(condition, user_message, context)
        elif condition_type == "sentiment":
            return await self._evaluate_sentiment(condition, user_message, context)
        
        return False
    
    async def _evaluate_contains(self, condition: Dict[str, Any], user_message: str, context: Dict[str, Any]) -> bool:
        """Check if user message contains specific keywords"""
        keywords = condition.get("keywords", [])
        case_sensitive = condition.get("case_sensitive", False)
        
        message = user_message if case_sensitive else user_message.lower()
        
        for keyword in keywords:
            keyword = keyword if case_sensitive else keyword.lower()
            if keyword in message:
                return True
        
        return False
    
    async def _evaluate_regex(self, condition: Dict[str, Any], user_message: str, context: Dict[str, Any]) -> bool:
        """Check if user message matches regex pattern"""
        pattern = condition.get("pattern", "")
        flags = re.IGNORECASE if not condition.get("case_sensitive", False) else 0
        
        try:
            return bool(re.search(pattern, user_message, flags))
        except re.error:
            logging.error(f"Invalid regex pattern: {pattern}")
            return False
    
    async def _evaluate_intent(
        self,
        condition: Dict[str, Any],
        user_message: str,
        context: Dict[str, Any],
        ai_response: Optional[str]
    ) -> bool:
        """Evaluate based on detected intent (placeholder)"""
        # This could integrate with intent recognition services
        target_intents = condition.get("intents", [])
        detected_intent = context.get("detected_intent", "")
        
        return detected_intent in target_intents
    
    async def _evaluate_context(self, condition: Dict[str, Any], user_message: str, context: Dict[str, Any]) -> bool:
        """Evaluate based on conversation context"""
        context_key = condition.get("context_key", "")
        expected_value = condition.get("expected_value")
        operator = condition.get("operator", "equals")
        
        actual_value = context.get(context_key)
        
        if operator == "equals":
            return actual_value == expected_value
        elif operator == "contains":
            return expected_value in str(actual_value) if actual_value else False
        elif operator == "greater_than":
            return float(actual_value) > float(expected_value) if actual_value else False
        elif operator == "less_than":
            return float(actual_value) < float(expected_value) if actual_value else False
        
        return False
    
    async def _evaluate_sentiment(self, condition: Dict[str, Any], user_message: str, context: Dict[str, Any]) -> bool:
        """Evaluate based on message sentiment (placeholder)"""
        # This could integrate with sentiment analysis services
        target_sentiment = condition.get("sentiment", "neutral")
        detected_sentiment = context.get("sentiment", "neutral")
        
        return detected_sentiment == target_sentiment
    
    def _find_node(self, nodes: List[Dict[str, Any]], node_id: str) -> Optional[Dict[str, Any]]:
        """Find a node by ID"""
        for node in nodes:
            if node.get("id") == node_id:
                return node
        return None
    
    def _replace_variables(self, template: str, user_message: str, context: Dict[str, Any]) -> str:
        """Replace variables in message templates"""
        
        # Replace common variables
        replacements = {
            "{{user_message}}": user_message,
            "{{user_name}}": context.get("user_name", "there"),
            "{{user_id}}": context.get("user_id", ""),
            "{{channel}}": context.get("channel", ""),
        }
        
        # Replace context variables
        for key, value in context.items():
            replacements[f"{{{{context.{key}}}}}"] = str(value)
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result