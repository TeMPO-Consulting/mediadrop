function getXMLHttpRequest() {
        var xhr = null;
        if (window.XMLHttpRequest || window.ActiveXObject) {
            if (window.ActiveXObject) {
                try {
                    xhr = new ActiveXObject("Msxml2.XMLHTTP");
                } catch (e) {
                    xhr = new ActiveXObject("Microsoft.XMLHTTP");
                }
            } else {
                xhr = new XMLHttpRequest();
            }
        } else {
            return null;
        }
        return xhr;
    }

function incrementViews(slug) {
    console.log(localStorage.getItem("axitube_" + slug)); 
    if (localStorage.getItem("axitube_" + slug) != "true") {
        localStorage.setItem("axitube_" + slug, "true");
        var xhttp = getXMLHttpRequest();
        xhttp.onreadystatechange = function() {                             
            if (xhttp.readyState === 4 && xhttp.status === 200) {          
                document.getElementById("media_views").innerHTML = xhttp.responseText;
            }                                                               
        }                                                                   
        xhttp.open("GET", "/media/" + slug + "/increment_views", true);                 
        xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhttp.send();                        
    }                                                                       
}

incrementViews(document.querySelector('meta[property="og:slug"]').content);
