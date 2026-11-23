// Erros HTTP: o corpo continua sendo texto puro, como no contrato original.
class HttpError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}

const badRequest = (message = 'Bad Request') => new HttpError(400, message);
const unauthorized = (message = 'Não autorizado') => new HttpError(401, message);
const forbidden = (message = 'Acesso negado') => new HttpError(403, message);
const notFound = (message) => new HttpError(404, message);

module.exports = { HttpError, badRequest, unauthorized, forbidden, notFound };
