// CORS fechado por padrão: sem origens configuradas, nenhum header é enviado.
function createCors(allowedOrigins) {
    const allowAll = allowedOrigins.includes('*');
    return (req, res, next) => {
        const origin = req.get('origin');
        if (!origin || !(allowAll || allowedOrigins.includes(origin))) return next();
        res.set('Access-Control-Allow-Origin', allowAll ? '*' : origin);
        if (!allowAll) res.vary('Origin');
        res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
        res.set('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
        if (req.method === 'OPTIONS') return res.sendStatus(204);
        next();
    };
}

module.exports = { createCors };
