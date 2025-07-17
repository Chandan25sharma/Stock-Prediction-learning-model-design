# Deploying Stock Trading Agent to Vercel

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally with `npm install -g vercel`
3. **Git Repository**: Your code should be in a Git repository

## Deployment Steps

### Method 1: Using Vercel CLI (Recommended)

1. **Navigate to your project directory:**
   ```bash
   cd realtime-agent
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy the application:**
   ```bash
   vercel --prod
   ```

4. **Follow the prompts:**
   - Choose "Link to existing project?" → No
   - Choose "What's your project's name?" → stock-trading-agent
   - Choose "In which directory is your code located?" → ./

### Method 2: Using GitHub Integration

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Go to Vercel Dashboard:**
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository

3. **Configure Build Settings:**
   - Framework Preset: Other
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: pip install -r requirements.txt

4. **Deploy:**
   - Click "Deploy"
   - Wait for deployment to complete

## Configuration Files

The following files are required for Vercel deployment:

### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHONPATH": "/var/task"
  }
}
```

### `api/index.py`
- Contains the Flask application adapted for Vercel
- Embedded HTML template (no separate template files needed)
- Handles all routes and API endpoints

### `requirements.txt`
- Lists all Python dependencies
- Optimized for Vercel's Python runtime

## Environment Variables

If you need to add environment variables:

1. **In Vercel Dashboard:**
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add your variables

2. **In your code:**
   ```python
   import os
   SECRET_KEY = os.environ.get('SECRET_KEY', 'default-value')
   ```

## Troubleshooting

### Common Issues:

1. **Build Timeout:**
   - Reduce dependencies in requirements.txt
   - Use lighter versions of libraries

2. **Memory Limit:**
   - Optimize model size
   - Use model compression techniques

3. **Cold Start:**
   - Vercel functions have cold start delays
   - Consider using caching for frequently accessed data

4. **File System:**
   - Vercel is read-only after deployment
   - Use temporary files or external storage for persistence

### Debugging:

1. **Check Vercel Logs:**
   ```bash
   vercel logs [deployment-url]
   ```

2. **Local Testing:**
   ```bash
   vercel dev
   ```

3. **Function Logs:**
   - View real-time logs in Vercel dashboard
   - Check for Python errors and warnings

## Performance Optimization

1. **Model Size:**
   - Use smaller model files
   - Consider model quantization

2. **Dependencies:**
   - Remove unused packages
   - Use lighter alternatives

3. **Caching:**
   - Implement response caching
   - Use CDN for static assets

## Deployment Checklist

- [ ] `vercel.json` file created
- [ ] `api/index.py` file created
- [ ] `requirements.txt` updated
- [ ] `.vercelignore` file created
- [ ] Environment variables set (if needed)
- [ ] Domain configured (optional)
- [ ] SSL certificate enabled (automatic)

## Post-Deployment

1. **Test the Application:**
   - Visit your Vercel URL
   - Test all functionality
   - Check API endpoints

2. **Monitor Performance:**
   - Check function execution times
   - Monitor error rates
   - Review usage statistics

3. **Custom Domain (Optional):**
   - Add your custom domain in Vercel dashboard
   - Configure DNS settings

## Scaling Considerations

1. **Function Limits:**
   - Execution time: 10 seconds (hobby), 5 minutes (pro)
   - Memory: 1GB (hobby), 3GB (pro)
   - Bandwidth: 100GB (hobby), 1TB (pro)

2. **Concurrent Requests:**
   - Vercel automatically scales
   - No manual configuration needed

3. **Database:**
   - Consider external database for persistence
   - Use Redis for caching

## Security

1. **API Keys:**
   - Use environment variables
   - Never commit secrets to Git

2. **CORS:**
   - Configure appropriate CORS settings
   - Restrict origins if needed

3. **Rate Limiting:**
   - Implement rate limiting for API endpoints
   - Use Vercel's edge functions for protection

## Support

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Python Runtime**: [vercel.com/docs/functions/serverless-functions/runtimes/python](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- **GitHub Issues**: Create issues for bugs and feature requests
