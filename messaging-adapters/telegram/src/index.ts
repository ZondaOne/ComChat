import TelegramBot from 'node-telegram-bot-api';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN!;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const TENANT_SLUG = process.env.TENANT_SLUG || 'demo';

if (!BOT_TOKEN) {
  console.error('TELEGRAM_BOT_TOKEN is required');
  process.exit(1);
}

const bot = new TelegramBot(BOT_TOKEN, { polling: true });

console.log('🤖 Telegram Bot started');

// Handle text messages
bot.on('message', async (msg) => {
  if (msg.text && !msg.text.startsWith('/')) {
    await handleMessage(msg);
  }
});

// Handle photo messages
bot.on('photo', async (msg) => {
  await handlePhotoMessage(msg);
});

async function handleMessage(msg: TelegramBot.Message) {
  const chatId = msg.chat.id;
  const userId = msg.from?.id.toString() || 'unknown';
  const message = msg.text || '';

  try {
    // Send typing indicator
    await bot.sendChatAction(chatId, 'typing');

    // Send to ComChat backend
    const response = await axios.post(`${BACKEND_URL}/api/v1/chat/send`, {
      message,
      channel: 'telegram',
      channel_user_id: userId,
      tenant_slug: TENANT_SLUG,
    });

    // Send response back to user
    await bot.sendMessage(chatId, response.data.response);

  } catch (error) {
    console.error('Error processing message:', error);
    await bot.sendMessage(chatId, 'Sorry, I encountered an error. Please try again.');
  }
}

async function handlePhotoMessage(msg: TelegramBot.Message) {
  const chatId = msg.chat.id;
  const userId = msg.from?.id.toString() || 'unknown';
  const caption = msg.caption || 'Image shared';

  try {
    // Send typing indicator
    await bot.sendChatAction(chatId, 'typing');

    // Get the largest photo
    const photo = msg.photo?.[msg.photo.length - 1];
    if (!photo) return;

    // Get file URL
    const file = await bot.getFile(photo.file_id);
    const mediaUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${file.file_path}`;

    // Send to ComChat backend
    const response = await axios.post(`${BACKEND_URL}/api/v1/chat/send`, {
      message: caption,
      channel: 'telegram',
      channel_user_id: userId,
      tenant_slug: TENANT_SLUG,
      media_url: mediaUrl,
      media_type: 'image/jpeg',
    });

    // Send response back to user
    await bot.sendMessage(chatId, response.data.response);

  } catch (error) {
    console.error('Error processing photo:', error);
    await bot.sendMessage(chatId, 'Sorry, I encountered an error processing your image.');
  }
}

// Handle start command
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, `👋 Welcome to ComChat!\n\nI'm an AI assistant powered by GPT. You can:\n• Send me text messages\n• Share images for analysis\n• Ask me questions\n\nJust start typing!`);
});

// Handle help command  
bot.onText(/\/help/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, `ℹ️ ComChat Help\n\n• Just send me any message to chat\n• Share images and I'll analyze them\n• I'm powered by OpenAI GPT models\n\nFor support, contact your administrator.`);
});

// Error handling
bot.on('polling_error', (error) => {
  console.error('Polling error:', error);
});

process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down Telegram bot...');
  bot.stopPolling();
  process.exit(0);
});