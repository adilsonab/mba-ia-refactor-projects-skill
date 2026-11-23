const { DEFAULT_ROLE } = require('../config/constants');

const STATEMENTS = [
    'PRAGMA foreign_keys = ON',
    `CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        pass TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT '${DEFAULT_ROLE}'
    )`,
    'CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL, active INTEGER NOT NULL DEFAULT 1)',
    `CREATE TABLE enrollments (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        course_id INTEGER NOT NULL REFERENCES courses(id)
    )`,
    `CREATE TABLE payments (
        id INTEGER PRIMARY KEY,
        enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
        amount REAL NOT NULL,
        status TEXT NOT NULL
    )`,
    'CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT NOT NULL, created_at DATETIME NOT NULL)',
    'CREATE INDEX idx_enrollments_course ON enrollments(course_id)',
    'CREATE INDEX idx_enrollments_user ON enrollments(user_id)',
    'CREATE INDEX idx_payments_enrollment ON payments(enrollment_id)',
];

async function applySchema(db) {
    for (const sql of STATEMENTS) {
        await db.run(sql);
    }
}

module.exports = { applySchema };
