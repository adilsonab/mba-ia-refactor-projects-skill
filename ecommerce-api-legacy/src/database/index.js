const sqlite3 = require('sqlite3');
const { hashPassword } = require('../utils/password');
const { PAYMENT_STATUS } = require('../config/constants');

const SCHEMA = [
    'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)',
    'CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)',
    'CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)',
    'CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)',
    'CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)',
];

function openConnection(path) {
    return new Promise((resolve, reject) => {
        const conn = new sqlite3.Database(path, (err) => (err ? reject(err) : resolve(conn)));
    });
}

// Envolve a conexão sqlite3 (callbacks) em uma API baseada em Promises.
function wrap(conn) {
    const run = (sql, params = []) => new Promise((resolve, reject) => {
        conn.run(sql, params, function onRun(err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
    const get = (sql, params = []) => new Promise((resolve, reject) => {
        conn.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });
    const all = (sql, params = []) => new Promise((resolve, reject) => {
        conn.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });
    const close = () => new Promise((resolve, reject) => conn.close((err) => (err ? reject(err) : resolve())));

    // Conexão única: transações são serializadas em uma fila para não se intercalarem.
    let queue = Promise.resolve();
    function transaction(work) {
        const result = queue.then(async () => {
            await run('BEGIN');
            try {
                const value = await work();
                await run('COMMIT');
                return value;
            } catch (err) {
                await run('ROLLBACK');
                throw err;
            }
        });
        queue = result.catch(() => {});
        return result;
    }

    return { run, get, all, close, transaction };
}

async function initSchema(db) {
    for (const statement of SCHEMA) {
        await db.run(statement);
    }
}

async function seed(db) {
    await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')]);
    await db.run('INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)',
        ['Clean Architecture', 997.0, 'Docker', 497.0]);
    await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
    await db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [1, 997.0, PAYMENT_STATUS.PAID]);
}

async function createDatabase(path = ':memory:') {
    const db = wrap(await openConnection(path));
    await initSchema(db);
    await seed(db);
    return db;
}

module.exports = { createDatabase };
