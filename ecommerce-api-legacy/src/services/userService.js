const { NotFoundError } = require('../middlewares/errorHandler');

function createUserService({ db, userModel, enrollmentModel, paymentModel }) {
    return {
        // Cascata transacional (AP-20): pagamentos → matrículas → usuário. Nada fica órfão
        // e, se qualquer passo falhar, nada é removido.
        deleteUser(id) {
            return db.transaction(async () => {
                if (!(await userModel.findById(id))) throw new NotFoundError('Usuário não encontrado');
                await paymentModel.deleteByUser(id);
                await enrollmentModel.deleteByUser(id);
                await userModel.deleteById(id);
            });
        },
    };
}

module.exports = { createUserService };
