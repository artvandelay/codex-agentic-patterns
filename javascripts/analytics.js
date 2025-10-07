// Google tag (gtag.js) - Load the script first
var script = document.createElement('script');
script.async = true;
script.src = 'https://www.googletagmanager.com/gtag/js?id=G-XBHSYKB0D3';
document.head.appendChild(script);

// Initialize gtag after script loads
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', 'G-XBHSYKB0D3');
