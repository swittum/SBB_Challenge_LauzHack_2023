// static/slideshow.js

var slideIndex = 0;
var slides = document.getElementsByClassName("mySlides");

function showSlides() {
    for (var i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }

    slideIndex++;

    if (slideIndex > slides.length) {
        slideIndex = 1;
    }

    slides[slideIndex - 1].style.display = "block";
}

// Run the slideshow every 3 seconds
setInterval(function () {
    showSlides();
}, 3000);

// Reset slideIndex to 0 when reaching the end
function resetIndex() {
    slideIndex = 0;
}

// Reset slideIndex after all images are loaded
document.addEventListener('DOMContentLoaded', function () {
    resetIndex();
});
