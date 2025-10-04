import { Router } from 'express';

const router = Router();

// Example route
router.get('/', (req, res) => {
    res.json({ message: 'Welcome to the API' });
});

// Example POST route
router.post('/test', (req, res) => {
    res.json({ message: 'Test endpoint', data: req.body });
});

export default router;
