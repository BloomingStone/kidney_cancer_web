var container = document.querySelector("#unity-container");
var canvas = document.querySelector("#unity-canvas");
var loadingBar = document.querySelector("#unity-loading-bar");
var progressBarFull = document.querySelector("#unity-progress-bar-full");
//var fullscreenButton = document.querySelector("#unity-fullscreen-button");
var warningBanner = document.querySelector("#unity-warning");

// Shows a temporary message banner/ribbon for a few seconds, or
// a permanent error message on top of the canvas if type=='error'.
// If type=='warning', a yellow highlight color is used.
// Modify or remove this function to customize the visually presented
// way that non-critical warnings and error messages are presented to the
// user.

function unityShowBanner(msg, type) {
    function updateBannerVisibility() {
        warningBanner.style.display = warningBanner.children.length ? 'block' : 'none';
    }
    var div = document.createElement('div');
    div.innerHTML = msg;
    warningBanner.appendChild(div);
    if (type == 'error') div.style = 'background: red; padding: 10px;';
    else {
        if (type == 'warning') div.style = 'background: yellow; padding: 10px;';
        setTimeout(function() {
            warningBanner.removeChild(div);
            updateBannerVisibility();
        }, 5000);
    }
    updateBannerVisibility();
}

var buildUrl = "/static/build/Build";
var loaderUrl = buildUrl + "/Release.loader.js";
var config = {
    dataUrl: "/gz/Release.data.gz",
    frameworkUrl: "/gz/Release.framework.js.gz",
    codeUrl: "/gz/Release.wasm.gz",
    streamingAssetsUrl: "/static/build/StreamingAssets",
    companyName: "DefaultCompany",
    productName: "Viewer",
    productVersion: "1.0",
    showBanner: unityShowBanner,
};

// var buildUrl = "/static/build/Build";
// var loaderUrl = buildUrl + "/Build.loader.js";
// var config = {
//   dataUrl: buildUrl + "/Build.data",
//   frameworkUrl: buildUrl + "/Build.framework.js",
//   codeUrl: buildUrl + "/Build.wasm",
//   streamingAssetsUrl: "/static/build/StreamingAssets",
//   companyName: "DefaultCompany",
//   productName: "Viewer",
//   productVersion: "1.0",
//   showBanner: unityShowBanner,
// };

// By default Unity keeps WebGL canvas render target size matched with
// the DOM size of the canvas element (scaled by window.devicePixelRatio)
// Set this to false if you want to decouple this synchronization from
// happening inside the engine, and you would instead like to size up
// the canvas DOM size and WebGL render target sizes yourself.
// config.matchWebGLToCanvasSize = false;

if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
    container.className = "unity-mobile";
    // Avoid draining fillrate performance on mobile devices,
    // and default/override low DPI mode on mobile browsers.
    config.devicePixelRatio = 1;
    unityShowBanner('WebGL builds are not supported on mobile devices.');
} else {
    canvas.style.width = "960px";
    canvas.style.height = "600px";
}
loadingBar.style.display = "block";

var script = document.createElement("script");
script.src = loaderUrl;
script.onload = () => {
    createUnityInstance(canvas, config, (progress) => {
        progressBarFull.style.width = 100 * progress + "%";
    }).then((unityInstance) => {
        loadingBar.style.display = "none";
    }).catch((message) => {
        alert(message);
    });
};
document.body.appendChild(script);


var html="<a class='btn btn-secondary' id='report-btn' data-bs-toggle='offcanvas' href='#offcanvasExample' role='button' aria-controls='offcanvasExample' >CT report</a>";

setTimeout("document.getElementById('show-delay').innerHTML=html",5000);//延时10秒


    toastr.options = {
        closeButton: true,
        debug: true,
        progressBar: true,
        positionClass: "toast-top-center",
        onclick: null,
        showDuration: "300",
        hideDuration: "1000",
        timeOut: "2000",
        extendedTimeOut: "1000",
        showEasing: "swing",
        hideEasing: "linear",
        showMethod: "fadeIn",
        hideMethod: "fadeOut"
    };


function submit_report() {
    $.ajax({
        cache: false,
        url: "/image-report/",
        type: "POST",
        dataType: "json",
        data: {
            "observation": $("#observation").val(),
            "impression": $("#impression").val(),
        },
        async: false,
        success: function(data) {
            console.log(data);
            if (data.status == "200") {
                toastr.success('提交成功');

            }
        },
    });
};


function noright(obj) {
    if (obj) {
        obj.oncontextmenu  =  function() {
            return false;
        }
        obj.ondragstart  =  function() {
            return false;
        }
        obj.onselectstart  =  function() {
            return false;
        }
        obj.onselect  =  function() {
            obj.selection.empty();
        }
        obj.oncopy  =  function() {
            obj.selection.empty();
        }
        obj.onbeforecopy  =  function() {
            return false;
        }
    }
}

setInterval(function () { //每5秒刷新一次图表
document.oncontextmenu = function(){

    return false;

}

    }, 3000);