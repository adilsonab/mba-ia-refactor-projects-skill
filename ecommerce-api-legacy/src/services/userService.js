function createUserService({ db, userModel }) {
    return {
        // Comportamento preservado: matrículas e pagamentos do usuário NÃO são removidos
        // (ver pendência AP-20 no relatório de auditoria).
        deleteUser(id) {
            return db.transaction(() => userModel.deleteById(id));
        },
    };
}

module.exports = { createUserService };
