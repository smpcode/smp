/**
 * Get the user IP throught the webkitRTCPeerConnection
 * @param onNewIP {Function} listener function to expose the IP locally
 * @return undefined
 */
export function getUserIP(onNewIP) { //  onNewIp - your listener function for new IPs
    //compatibility for firefox and chrome
    let myPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection;
    let pc = new myPeerConnection({
            iceServers: []
        }),
        noop = function() {},
        localIPs = {},
        ipRegex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/g,
        key;

    function iterateIP(ip) {
        if (!localIPs[ip]) onNewIP(ip);
        localIPs[ip] = true;
    }

    //create a bogus data channel
    pc.createDataChannel("");

    // create offer and set local description
    pc.createOffer(function(sdp) {
        sdp.sdp.split('\n').forEach(function(line) {
            if (line.indexOf('candidate') < 0) return;
            line.match(ipRegex).forEach(iterateIP);
        });

        pc.setLocalDescription(sdp, noop, noop);
    }, noop);

    //listen for candidate events
    pc.onicecandidate = function(ice) {
        if (!ice || !ice.candidate || !ice.candidate.candidate || !ice.candidate.candidate.match(ipRegex)) return;
        ice.candidate.candidate.match(ipRegex).forEach(iterateIP);
    };
}

function unitToBytes(unit) {
    let unitBytes = parseInt(unit);
    let unitName = unit.substr(unit.length - 2);
    switch (unitName) {
        case "kb":
            unitBytes = unitBytes * 1024;
            break;
        case "mb":
            unitBytes = unitBytes * 1024 * 1024;
            break;
        case "gb":
            unitBytes = unitBytes * 1024 * 1024 * 1024;
            break;
        case "tb":
            unitBytes = unitBytes * 1024 * 1024 * 1024;
            break;
    }
    return unitBytes;
}

// 带单位计算的排序方式
export function sortByUnitSize(a, b) {
    let aSize = unitToBytes(a);
    let bSize = unitToBytes(b);
    return aSize > bSize;
}
