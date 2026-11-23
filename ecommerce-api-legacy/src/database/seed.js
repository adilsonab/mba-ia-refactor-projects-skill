const { PAYMENT_STATUS, ROLES } = require('../config/constants');
const { hashPassword, generatePassword } = require('../utils/password');

// Dados de desenvolvimento do seed original (Leonan / 123, agora com hash) + um admin.
async function seed(db, { adminEmail, adminPassword }, logger) {
    let effectiveAdminPassword = adminPassword;
    if (!effectiveAdminPassword) {
        effectiveAdminPassword = generatePassword(); // nunca logada
        logger.warn('ADMIN_PASSWORD não definida: login do admin desabilitado na prática até definir a variável.');
    }

    await db.transaction(async () => {
        await db.run('INSERT INTO users (name, email, pass, role) VALUES (?, ?, ?, ?)',
            ['Leonan', 'leonan@fullcycle.com.br', await hashPassword('123'), ROLES.STUDENT]);
        await db.run('INSERT INTO users (name, email, pass, role) VALUES (?, ?, ?, ?)',
            ['Administrador', adminEmail.toLowerCase(), await hashPassword(effectiveAdminPassword), ROLES.ADMIN]);
        await db.run('INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)',
            ['Clean Architecture', 997.0, 'Docker', 497.0]);
        await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
        await db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (1, ?, ?)', [997.0, PAYMENT_STATUS.PAID]);
    });
}

module.exports = { seed };
