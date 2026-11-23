const { notFound } = require('../utils/errors');

function createUserService({ db, models }) {
    const { userModel, enrollmentModel, paymentModel } = models;

    // Matrículas e pagamentos pertencem ao usuário: exclusão em cascata na mesma transação.
    async function deleteUser(id) {
        return db.transaction(async () => {
            const user = await userModel.findById(id);
            if (!user) throw notFound('Usuário não encontrado');
            await paymentModel.deleteByUser(id);
            await enrollmentModel.deleteByUser(id);
            await userModel.deleteById(id);
        });
    }

    return { deleteUser };
}

module.exports = { createUserService };
