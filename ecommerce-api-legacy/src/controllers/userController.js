const { parsePositiveId } = require('./validators');

// O texto original ("...as matrículas e pagamentos ficaram sujos no banco") descrevia o defeito
// corrigido (AP-20): agora a exclusão remove matrículas e pagamentos na mesma transação.
const DELETE_MESSAGE = 'Usuário deletado, junto com suas matrículas e pagamentos.';

function createUserController({ userService }) {
    return {
        async deleteUser(req, res) {
            await userService.deleteUser(parsePositiveId(req.params.id));
            res.send(DELETE_MESSAGE);
        },
    };
}

module.exports = { createUserController };
