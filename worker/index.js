const express = require('express');
const cors = require('cors');
const redis = require('ioredis');

const app = express();
app.use(cors());
app.use(express.json());

// Redis client
const redisClient = new redis({
  host: process.env.REDIS_HOST || 'redis',
  port: process.env.REDIS_PORT || 6379,
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', service: 'worker' });
});

// Worker task processing
app.post('/process', async (req, res) => {
  try {
    const { task } = req.body;
    
    // Simulate task processing
    console.log('Processing task:', task);
    
    // Store result in Redis
    await redisClient.set(`task:${Date.now()}`, JSON.stringify({
      task,
      status: 'completed',
      timestamp: new Date().toISOString()
    }));
    
    res.json({ status: 'success', message: 'Task processed' });
  } catch (error) {
    console.error('Error processing task:', error);
    res.status(500).json({ error: 'Task processing failed' });
  }
});

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Worker service running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  redisClient.disconnect();
  process.exit(0);
});