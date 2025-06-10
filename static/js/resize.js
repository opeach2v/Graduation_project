function resizeToMin(w, h) {
    w = w > window.outerWidth || w < window.outerWidth ? w : window.outerWidth;
    h = h > window.outerHeight || h < window.outerHeight ? h : window.outerHeight;
    window.resizeTo(w, h);
};

window.addEventListener('resize', function() { resizeToMin(800, 650); });