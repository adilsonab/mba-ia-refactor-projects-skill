const DELETE_MESSAGE = 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.';

function createUserController({ userService }) {
    return {
        async deleteUser(req, res) {
            await userService.deleteUser(req.params.id);
            res.send(DELETE_MESSAGE);
        },
    };
}

module.exports = { createUserController };
