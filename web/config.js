// En producción pega la URL de tu Worker sin /api/state ni barra final.
// Vacío = instantáneas de GitHub Actions, que pueden retrasarse.
window.TRAINS_CONFIG = { apiBase: ['localhost','127.0.0.1'].includes(location.hostname) ? location.origin : '' };
