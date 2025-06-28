import React, { useState, useEffect } from 'react';
import { PlusIcon, PlayIcon, PauseIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { Button, Loading } from '../common';
import { Workflow } from '../../types';

interface WorkflowManagerProps {
  domain?: string;
}

const WorkflowManager: React.FC<WorkflowManagerProps> = ({ domain = 'general' }) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);

  useEffect(() => {
    loadWorkflows();
  }, [domain]);

  const loadWorkflows = async () => {
    setLoading(true);
    try {
      // Mock data for demonstration
      const mockWorkflows: Workflow[] = [
        {
          id: '1',
          name: 'Customer Support Triage',
          domain: 'support',
          description: 'Automatically categorize and route customer inquiries',
          status: 'active',
          execution_count: 152,
          success_rate: 0.94
        },
        {
          id: '2',
          name: 'Healthcare Consultation',
          domain: 'healthcare',
          description: 'HIPAA-compliant patient consultation workflow',
          status: 'active',
          execution_count: 89,
          success_rate: 0.97
        },
        {
          id: '3',
          name: 'Financial Advisory',
          domain: 'finance',
          description: 'SOX-compliant financial advice workflow',
          status: 'draft',
          execution_count: 12,
          success_rate: 0.83
        }
      ];
      
      setWorkflows(mockWorkflows);
    } catch (error) {
      toast.error('Failed to load workflows');
    } finally {
      setLoading(false);
    }
  };

  const executeWorkflow = async (workflow: Workflow) => {
    try {
      toast.loading('Executing workflow...', { id: 'execute' });
      
      // Mock execution
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success(`Workflow "${workflow.name}" executed successfully`, { id: 'execute' });
    } catch (error) {
      toast.error('Failed to execute workflow', { id: 'execute' });
    }
  };

  const toggleWorkflowStatus = async (workflow: Workflow) => {
    try {
      const newStatus = workflow.status === 'active' ? 'paused' : 'active';
      
      setWorkflows(prev => 
        prev.map(w => w.id === workflow.id ? { ...w, status: newStatus } : w)
      );
      
      toast.success(`Workflow ${newStatus}`);
    } catch (error) {
      toast.error('Failed to update workflow status');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'paused': return 'text-yellow-600 bg-yellow-100';
      case 'draft': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return <Loading size="lg" className="py-8" />;
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Workflow Manager</h2>
          <p className="text-gray-600">Domain: {domain}</p>
        </div>
        <Button variant="primary">
          <PlusIcon className="w-4 h-4 mr-2" />
          Create Workflow
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {workflows.map((workflow) => (
          <div
            key={workflow.id}
            className="bg-white rounded-lg shadow-md border hover:shadow-lg transition-shadow cursor-pointer"
            onClick={() => setSelectedWorkflow(workflow)}
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  {workflow.name}
                </h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(workflow.status)}`}>
                  {workflow.status}
                </span>
              </div>
              
              <p className="text-gray-600 text-sm mb-4">
                {workflow.description}
              </p>
              
              <div className="flex justify-between text-sm text-gray-500 mb-4">
                <span>Executions: {workflow.execution_count}</span>
                <span>Success: {(workflow.success_rate * 100).toFixed(1)}%</span>
              </div>
              
              <div className="flex space-x-2">
                <Button
                  size="sm"
                  variant="primary"
                  onClick={(e) => {
                    e.stopPropagation();
                    executeWorkflow(workflow);
                  }}
                >
                  <PlayIcon className="w-4 h-4 mr-1" />
                  Execute
                </Button>
                
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleWorkflowStatus(workflow);
                  }}
                >
                  {workflow.status === 'active' ? (
                    <PauseIcon className="w-4 h-4" />
                  ) : (
                    <PlayIcon className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {workflows.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No workflows found for this domain</p>
          <Button variant="primary" className="mt-4">
            <PlusIcon className="w-4 h-4 mr-2" />
            Create Your First Workflow
          </Button>
        </div>
      )}

      {/* Workflow Details Modal */}
      {selectedWorkflow && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-900">
                  {selectedWorkflow.name}
                </h3>
                <button
                  onClick={() => setSelectedWorkflow(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <p className="text-gray-600">{selectedWorkflow.description}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Domain</label>
                    <p className="text-gray-900">{selectedWorkflow.domain}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Status</label>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedWorkflow.status)}`}>
                      {selectedWorkflow.status}
                    </span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Executions</label>
                    <p className="text-gray-900">{selectedWorkflow.execution_count}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Success Rate</label>
                    <p className="text-gray-900">{(selectedWorkflow.success_rate * 100).toFixed(1)}%</p>
                  </div>
                </div>
              </div>
              
              <div className="flex justify-end space-x-2 mt-6">
                <Button variant="secondary" onClick={() => setSelectedWorkflow(null)}>
                  Close
                </Button>
                <Button variant="primary" onClick={() => executeWorkflow(selectedWorkflow)}>
                  Execute Workflow
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowManager;