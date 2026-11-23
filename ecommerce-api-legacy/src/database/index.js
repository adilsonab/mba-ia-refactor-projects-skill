const sqlite3 = require('sqlite3');
const { applySchema } = require('./schema');

// Wrapper Promise sobre a conexão sqlite3 + transações serializadas
// (a conexão é única, então transações concorrentes não podem se intercalar).
function wrap(connection) {
    const run = (sql, params = []) => new Promise((resolve, reject) => {
        connection.run(sql, params, function onRun(err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
    const get = (sql, params = []) => new Promise((resolve, reject) => {
        connection.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });
    const all = (sql, params = []) => new Promise((resolve, reject) => {
        connection.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });
    const close = () => new Promise((resolve, reject) => connection.close((err) => (err ? reject(err) : resolve())));

    let queue = Promise.resolve();
    const transaction = (work) => {
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
    };

    return { run, get, all, close, transaction };
}

async function createDatabase(filename = ':memory:') {
    const connection = await new Promise((resolve, reject) => {
        const conn = new sqlite3.Database(filename, (err) => (err ? reject(err) : resolve(conn)));
    });
    const db = wrap(connection);
    await applySchema(db);
    return db;
}

module.exports = { createDatabase };
