import express from 'express';
import axios from 'axios';
import dotenv from 'dotenv';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';
import crypto from 'crypto';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Environment variables
const WHATSAPP_ACCESS_TOKEN = process.env.WHATSAPP_ACCESS_TOKEN!;
const WHATSAPP_VERIFY_TOKEN = process.env.WHATSAPP_VERIFY_TOKEN!;
const WHATSAPP_PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID!;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const TENANT_SLUG = process.env.TENANT_SLUG || 'demo';
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());

// WhatsApp API base URL
const WHATSAPP_API_URL = `https://graph.facebook.com/v18.0/${WHATSAPP_PHONE_NUMBER_ID}/messages`;

console.log('🟢 WhatsApp Business API adapter starting...');

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'whatsapp-adapter',
    phone_number_id: WHATSAPP_PHONE_NUMBER_ID ? 'configured' : 'missing'
  });
});

// Webhook verification endpoint
app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === WHATSAPP_VERIFY_TOKEN) {
    console.log('✅ Webhook verified successfully');
    res.status(200).send(challenge);
  } else {
    console.log('❌ Webhook verification failed');
    res.status(403).send('Forbidden');
  }
});

// Webhook endpoint for receiving messages
app.post('/webhook', async (req, res) => {
  try {
    // Verify webhook signature
    if (WEBHOOK_SECRET && !verifyWebhookSignature(req.body, req.headers['x-hub-signature-256'] as string)) {
      console.log('❌ Invalid webhook signature');
      return res.status(401).send('Unauthorized');
    }

    const { entry } = req.body;

    if (!entry || !entry[0]) {
      return res.status(200).send('OK');
    }

    for (const change of entry[0].changes || []) {
      if (change.field === 'messages' && change.value) {
        await handleIncomingMessage(change.value);
      }
    }

    res.status(200).send('OK');
  } catch (error) {
    console.error('Error processing webhook:', error);
    res.status(500).send('Internal Server Error');
  }
});

async function handleIncomingMessage(messageData: any) {
  const { messages, contacts } = messageData;

  if (!messages || messages.length === 0) {
    return;
  }

  for (const message of messages) {
    try {
      const from = message.from;
      const messageId = message.id;
      const timestamp = message.timestamp;

      // Get contact info
      const contact = contacts?.find((c: any) => c.wa_id === from);
      const contactName = contact?.profile?.name || 'Unknown';

      // Handle different message types
      let messageContent = '';
      let mediaUrl = '';
      let mediaType = '';

      switch (message.type) {
        case 'text':
          messageContent = message.text.body;
          break;
        
        case 'image':
          messageContent = message.image.caption || 'Image shared';
          mediaUrl = await downloadWhatsAppMedia(message.image.id);
          mediaType = 'image/jpeg';
          break;
        
        case 'audio':
          messageContent = 'Audio message received';
          mediaUrl = await downloadWhatsAppMedia(message.audio.id);
          mediaType = 'audio/ogg';
          break;
        
        case 'video':
          messageContent = message.video.caption || 'Video shared';
          mediaUrl = await downloadWhatsAppMedia(message.video.id);
          mediaType = 'video/mp4';
          break;
        
        case 'document':
          messageContent = `Document shared: ${message.document.filename || 'file'}`;
          mediaUrl = await downloadWhatsAppMedia(message.document.id);
          mediaType = 'application/octet-stream';
          break;
        
        default:
          messageContent = `Unsupported message type: ${message.type}`;
      }

      // Send to ComChat backend
      const response = await axios.post(`${BACKEND_URL}/api/v1/chat/send`, {
        message: messageContent,
        channel: 'whatsapp',
        channel_user_id: from,
        tenant_slug: TENANT_SLUG,
        media_url: mediaUrl || undefined,
        media_type: mediaType || undefined,
        channel_message_id: messageId,
        user_name: contactName
      });

      // Send response back to WhatsApp
      if (response.data.response) {
        await sendWhatsAppMessage(from, response.data.response);
      }

    } catch (error) {
      console.error('Error processing message:', error);
      // Send error message to user
      await sendWhatsAppMessage(message.from, 'Sorry, I encountered an error. Please try again.');
    }
  }
}

async function sendWhatsAppMessage(to: string, message: string): Promise<void> {
  try {
    const payload = {
      messaging_product: 'whatsapp',
      to: to,
      type: 'text',
      text: {
        body: message
      }
    };

    await axios.post(WHATSAPP_API_URL, payload, {
      headers: {
        'Authorization': `Bearer ${WHATSAPP_ACCESS_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });

    console.log(`✅ Message sent to ${to}`);
  } catch (error) {
    console.error('Error sending WhatsApp message:', error);
    throw error;
  }
}

async function sendWhatsAppImage(to: string, imageUrl: string, caption?: string): Promise<void> {
  try {
    const payload = {
      messaging_product: 'whatsapp',
      to: to,
      type: 'image',
      image: {
        link: imageUrl,
        caption: caption
      }
    };

    await axios.post(WHATSAPP_API_URL, payload, {
      headers: {
        'Authorization': `Bearer ${WHATSAPP_ACCESS_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });

    console.log(`✅ Image sent to ${to}`);
  } catch (error) {
    console.error('Error sending WhatsApp image:', error);
    throw error;
  }
}

async function downloadWhatsAppMedia(mediaId: string): Promise<string> {
  try {
    // Get media URL from WhatsApp API
    const mediaResponse = await axios.get(
      `https://graph.facebook.com/v18.0/${mediaId}`,
      {
        headers: {
          'Authorization': `Bearer ${WHATSAPP_ACCESS_TOKEN}`
        }
      }
    );

    const mediaUrl = mediaResponse.data.url;

    // Download the media file
    const fileResponse = await axios.get(mediaUrl, {
      headers: {
        'Authorization': `Bearer ${WHATSAPP_ACCESS_TOKEN}`
      },
      responseType: 'arraybuffer'
    });

    // TODO: Upload to your own storage (S3, GCS, etc.)
    // For now, return the temporary URL
    return mediaUrl;

  } catch (error) {
    console.error('Error downloading WhatsApp media:', error);
    return '';
  }
}

function verifyWebhookSignature(payload: any, signature: string): boolean {
  if (!WEBHOOK_SECRET || !signature) {
    return false;
  }

  const expectedSignature = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(JSON.stringify(payload))
    .digest('hex');

  const receivedSignature = signature.replace('sha256=', '');

  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature, 'hex'),
    Buffer.from(receivedSignature, 'hex')
  );
}

// Template message support
app.post('/send-template', async (req, res) => {
  try {
    const { to, template_name, language, parameters } = req.body;

    const payload = {
      messaging_product: 'whatsapp',
      to: to,
      type: 'template',
      template: {
        name: template_name,
        language: {
          code: language || 'en'
        },
        components: parameters ? [
          {
            type: 'body',
            parameters: parameters.map((param: string) => ({
              type: 'text',
              text: param
            }))
          }
        ] : []
      }
    };

    await axios.post(WHATSAPP_API_URL, payload, {
      headers: {
        'Authorization': `Bearer ${WHATSAPP_ACCESS_TOKEN}`,
        'Content-Type': 'application/json'
      }
    });

    res.json({ success: true });
  } catch (error) {
    console.error('Error sending template:', error);
    res.status(500).json({ error: 'Failed to send template' });
  }
});

// Error handling
app.use((error: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 WhatsApp adapter running on port ${PORT}`);
  console.log(`📱 Phone Number ID: ${WHATSAPP_PHONE_NUMBER_ID || 'Not configured'}`);
  console.log(`🔗 Webhook URL: http://localhost:${PORT}/webhook`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down WhatsApp adapter...');
  process.exit(0);
});