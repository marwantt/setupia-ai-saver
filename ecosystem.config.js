module.exports = {
  apps: [{
    name: 'setupia-ai-saver',
    script: 'bot.py',
    interpreter: 'python3',
    cwd: '/Users/marwan/Desktop/Setupia AI Saver',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    },
    log_file: './logs/combined.log',
    out_file: './logs/out.log',
    error_file: './logs/error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};