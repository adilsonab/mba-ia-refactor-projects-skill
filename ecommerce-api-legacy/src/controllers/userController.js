const { parsePositiveInt } = require('../utils/validators');

function createUserController({ userService }) {
    return {
        async deleteUser(req, res) {
            const id = parsePositiveInt(req.params.id);
            await userService.deleteUser(id);
            res.send('Usuário deletado');
        },
    };
}

module.exports = { createUserController };
