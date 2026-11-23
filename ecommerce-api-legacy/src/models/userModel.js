function createUserModel(db) {
    return {
        findById: (id) => db.get('SELECT id, name, email, role FROM users WHERE id = ?', [id]),
        // Inclui o hash: uso exclusivo da verificação de credenciais, nunca serializado.
        findCredentialsByEmail: (email) => db.get('SELECT id, name, email, role, pass FROM users WHERE email = ?', [email]),
        async create({ name, email, passwordHash, role }) {
            const { lastID } = await db.run('INSERT INTO users (name, email, pass, role) VALUES (?, ?, ?, ?)',
                [name, email, passwordHash, role]);
            return lastID;
        },
        async deleteById(id) {
            const { changes } = await db.run('DELETE FROM users WHERE id = ?', [id]);
            return changes > 0;
        },
    };
}

module.exports = { createUserModel };
