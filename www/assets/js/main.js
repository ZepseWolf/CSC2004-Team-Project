var coverFile;
var payloadFile;
var encodedFile;
var isText;
var currentText = "Secret message"; 
var lsb = 7;
var encodedOrDecode ;

function initEncoder(){

  var coverDropEle = document.getElementById("cover-drag-area");
  var payloadDropEle = document.getElementById("payload-drag-area");
  

  coverDropEle.addEventListener('dragover', (event) => {
    event.preventDefault();
    coverDropEle.classList.add('active');
  });

  coverDropEle.addEventListener('dragleave', () => {
    coverDropEle.classList.remove('active');
    // dragTexts.forEach(function(dragText){
    //   dragText.textContent = 'Drag & Drop';

    // })
  });

  coverDropEle.addEventListener('drop', (event) => {
    event.preventDefault();
    coverDropEle.classList.toggle('active');
    // file = event.dataTransfer.files[0]; // grab single file even of user selects multiple files
    displayFile(coverDropEle,event.dataTransfer.files[0]);
    coverFile = event.dataTransfer.files[0];
  });

  payloadDropEle.addEventListener('dragover', (event) => {
    event.preventDefault();
    payloadDropEle.classList.add('active');
  });

  payloadDropEle.addEventListener('dragleave', () => {
    payloadDropEle.classList.remove('active');
    // dragTexts.forEach(function(dragText){
    //   dragText.textContent = 'Drag & Drop';

    // })
  });

  payloadDropEle.addEventListener('drop', (event) => {
    event.preventDefault();
    payloadDropEle.classList.toggle('active');
    // file = event.dataTransfer.files[0]; // grab single file even of user selects multiple files
    displayFile(payloadDropEle,event.dataTransfer.files[0]);
    payloadFile = event.dataTransfer.files[0];
  });

  const previewBtn = document.querySelector(".preview-btn");
  const preview = document.querySelector(".preview-overlay");
  const closeBtn = document.querySelector(".close-btn");
  const downloadBtn = document.getElementById("downloadBtn");

  previewBtn.addEventListener("click", function () {
    const loader = document.getElementById("loader");
    const displayResult = document.getElementById("displayResult");
    preview.classList.add("open-preview");
    loader.classList.remove("hide");
    displayResult.classList.add("content");
    downloadBtn.classList.add("content");
  });

  closeBtn.addEventListener("click", function () {
    preview.classList.remove("open-preview");
  });
}

function initDecoder() {

  var encodedDropEle = document.getElementById('encoded-drag-area')

  encodedDropEle.addEventListener('dragover', (event) => {
    event.preventDefault();
    encodedDropEle.classList.add('active');
  });

  encodedDropEle.addEventListener('dragleave', () => {
    encodedDropEle.classList.remove('active');
    // dragTexts.forEach(function (dragText) {
    //   dragText.textContent = 'Drag & Drop';

    // })
  });

  encodedDropEle.addEventListener('drop', (event) => {
    event.preventDefault();
    encodedDropEle.classList.toggle('active');
    // file = event.dataTransfer.files[0]; // grab single file even of user selects multiple files
    displayFile(encodedDropEle, event.dataTransfer.files[0]);
    encodedFile = event.dataTransfer.files[0];
  });

  const previewBtn = document.querySelector(".preview-btn");
  const preview = document.querySelector(".preview-overlay");
  const closeBtn = document.querySelector(".close-btn");

  previewBtn.addEventListener("click", function () {

    preview.classList.add("open-preview");
    loader.classList.remove("hide");
    displayResult.classList.add("content");
  });

  closeBtn.addEventListener("click", function () {
    preview.classList.remove("open-preview");
  });
}

function initProcessor(dropId){
  
  let input = document.createElement('input');
  input.type = 'file';
  input.onchange = () => {
    // you can use this method to get file and perform respective operations
    // let files =   Array.from(input.files);
    if(dropId == "encoded-drag-area"){
      encodedFile = input.files[0];
    }
    else if(dropId == "payload-drag-area"){
      payloadFile = input.files[0];
    }
    else if(dropId == "cover-drag-area" ){
      coverFile = input.files[0];
    }
    displayFile(document.getElementById(dropId),input.files[0]);
    // console.log(files);
  };
  input.click();
}

function displayFile(dropArea,file) {
  console.log(file);
  let fileType = file.type;
  let validExtensions = ['text/plain','image/jpeg', 'image/png', 'text/txt', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'audio/mpeg', 'video/mp4', 'video/x-msvideo', 'video/avi','audio/wav', 
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/pdf', 'application.vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'text/csv'];
  if(encodedOrDecode == "encode"){
    if (validExtensions.includes(fileType)) {
      blobToBase64(file).then((src) => {
        
        if (fileType == "image/jpeg" || fileType == 'image/png') {
          let imgTag = `<img src="${src}" alt="" width="100px">`;
          dropArea.innerHTML = imgTag;
        }
        else if (fileType == "audio/mpeg" || fileType == "audio/wav") {
          let audio = `<audio controls><source src="${src}" type="audio/mpeg">Your browser does not support the audio element.</audio>`;
          dropArea.innerHTML = audio;
        } 
        else if (fileType == "video/mp4" || fileType == "video/x-msvideo"|| fileType == "video/avi") {
          let video = `<video width="100%" height="100%" controls> <source src="${src}" type="video/mp4"> Your browser does not support the video tag. </video>`;
          dropArea.innerHTML = video;
        }
        else {
          console.log("this file type is :",fileType)
          let div = `<div>Inserted some file.</div>`;
          dropArea.innerHTML = div;
        }
        
      })
    } else {
      alert('This is not a supported file.');
      dropArea.classList.remove('active');
    }
  }
  else if (encodedOrDecode == "decode"){
    if (validExtensions.includes(fileType)) {
      blobToBase64(file).then((src) => {
        
        if (fileType == "image/jpeg" || fileType == 'image/png') {
          let imgTag = `<img src="${src}" alt="" width="100px">`;
          dropArea.innerHTML = imgTag;
        }
        else if (fileType == "audio/mpeg" || fileType == "audio/wav") {
          let audio = `<audio controls><source src="${src}" type="audio/mpeg">Your browser does not support the audio element.</audio>`;
          dropArea.innerHTML = audio;
        } 
        else if (fileType == "video/mp4" || fileType == "video/x-msvideo"|| fileType == "video/avi") {
          let video = `<div>Video here is current too big however you can still decode the hidden file by pressing the decode button.</div>`;
          dropArea.innerHTML = video;
        }
        else {
          console.log("this file type is :",fileType)
          let div = `<div>Inserted some file.</div>`;
          dropArea.innerHTML = div;
        }
        
      })
    } else {
      alert('This is not a supported file.');
      dropArea.classList.remove('active');
    }
  }
  
}

function changeString(textValue){
  currentText = textValue;
}

function showHideDiv(val){
  if(val ==1){ 
    isText = true;
    document.getElementById('div2').style.display='none'; 
    document.getElementById('div1').style.display='block'; 
  }

  if(val ==2){
    isText = false;
    document.getElementById('div1').style.display='none';
    document.getElementById('div2').style.display='block'; 
  }
}

function rangeSlide(value){
    // console.log('hi');
  lsb = value;
  const rangeValuesImage = document.querySelectorAll('.rangeValueImage');
  const inputImage = document.getElementById("input-Image");
  const rangeValuesText = document.querySelectorAll('.rangeValueText');
  const inputText = document.getElementById("input-Text");
  const rangeValuesVideo = document.querySelectorAll('.rangeValueVideo');
  const inputVideo = document.getElementById("input-Video");

  rangeValuesImage.forEach(function(rangeValue){
    if (rangeValue.dataset.value <= inputImage.value){
      rangeValue.classList.add("highlight");
    }else{
      rangeValue.classList.remove("highlight");
    }
  })

  rangeValuesText.forEach(function(rangeValue){
    if (rangeValue.dataset.value <= inputText.value){
      rangeValue.classList.add("highlight");
    }else{
      rangeValue.classList.remove("highlight");
    }
  })

  rangeValuesVideo.forEach(function(rangeValue){
    if (rangeValue.dataset.value <= inputVideo.value){
      rangeValue.classList.add("highlight");
    }else{
      rangeValue.classList.remove("highlight");
    }
  })
}

function processerFunction() {
  var originalImage = document.getElementById("original");
  var resultImage = document.getElementById("result");
  console.log(originalImage);
  window.onload = () => {
    var url = document.location.href;
    var params = url.split('?')[1].split('&');
    var data = {};
    var tmp;
    var imgTag;
    // console.log(url)
    // console.log(params)
    for (var i = 0; i < params.length; i++) {
      tmp = params[i].split('=');
      data = tmp[1];
      // data[tmp[0]] = tmp[1];
    }
    console.log(data);
    // console.log(data.data);
    if (data.includes('png') || data.includes('jpeg')) {
      console.log(`<img src="${data}"\>`);
      imgTag = `<img src="${data}"\>`;
      originalImage.innerHTML = imgTag;
    } else if (data.includes('txt') || data.includes('docs')) {
      console.log(`<img src="https://www.computerhope.com/jargon/t/text-file.png"\>`);
      imgTag = `<img src="https://www.computerhope.com/jargon/t/text-file.png"\>`;
      originalImage.innerHTML = imgTag;
      resultImage.innerHTML = imgTag;
    } else if (data.includes('mpeg') || data.includes('mp4') || data.includes('x-msvideo')) {
      console.log(`<video src="${data}"\>`);
      imgTag = `<video src="${data}"\>`;
      originalImage.innerHTML = imgTag;
    }
  }
}

function download(){
  alert("Downloaded in output folder!");
}

function goBack(){
  window.history.back();
}

function enterRoute(routeUrl,dataToSend){

  window.location.href = routeUrl+"?data="+dataToSend;
}

function submitToEel(){
  if(coverFile && lsb){
    var coverFileName = coverFile.name;
    
    blobToBase64(coverFile).then((coverBase64)=>{
      if(isText){
        console.log("current text",isText);
        eel.encodeFile(coverFileName,coverBase64,"file",currentText,isText,lsb)(displayOutputForEncoding);
      }
      else {
        var payloadFileName = payloadFile.name;
        blobToBase64(payloadFile).then((payloadBase64)=>{
          eel.encodeFile(coverFileName,coverBase64,payloadFileName,payloadBase64,isText,lsb)(displayOutputForEncoding);
        })
      }
      
    })
  }
  else if(encodedFile){
    var encodedFileName = encodedFile.name;
    if(encodedFileName.split(".")[1] == "mp4"){
      eel.decodeFile(encodedFileName,"meow",lsb)(displayOutput);
    }
    else{
      blobToBase64(encodedFile).then((encodedBase64)=>{
        eel.decodeFile(encodedFileName,encodedBase64,lsb)(displayOutput);
      })
    }
   
  }
  else{
    console.log("The require field is not met.")
  }
}

function displayOutputForEncoding(data){
  console.log(data);
  var loader = document.getElementById("loader");
  var displayResult = document.getElementById("displayResult");
  

  
  try {
    if(!data.fileName){
      throw ("There is an encoding error")
    }

    var fileName = data.fileName;
    var afterSrc = data.src;
    var afterEle = document.getElementById("afterElement")
    var beforeEle= document.getElementById("beforeElement")
    var downloadBtn = document.getElementById("downloadBtn");
    var beforeFileName = coverFile.name;
    var fileExtension = coverFile.name.split(".")[1]
    blobToBase64(coverFile).then(( beforeSrc )=>{
      let afterDiv=""
      let beforeDiv=""
      if(fileName == "text"){
        afterDiv = `<div style="color: black;">Decoded text : ${afterSrc}</div>`;
        beforeDiv = `<div style="color: black;">Decoded text : ${beforeSrc}</div>`;
      }
      else{
        if (fileExtension == "jpg" || fileExtension == 'png'|| fileExtension == 'jpeg') {
          afterDiv =`<img src="${afterSrc}" alt="" style="max-width: 100%;max-height:100%; height:auto;width:auto;" >`;
          beforeDiv =`<img src="${beforeSrc}" alt="" style="max-width: 100%;max-height:100%; height:auto;width:auto;">`;
        } else if (fileExtension == "mp3" || fileExtension == "wav") {
          afterDiv =`<audio controls><source src="${afterSrc}" type="audio/mpeg">Your browser does not support the audio element.</audio>`;
          beforeDiv =`<audio controls><source src="${beforeSrc}" type="audio/mpeg">Your browser does not support the audio element.</audio>`;
        } 
        else if (fileExtension == "mp4" || fileExtension == "avi") {
          afterDiv =`<div style="position: relative; top: -20px; padding: 10px; color: black;">Video ${fileName} is too big to display, however you can download it and find it in the output file.</div>`;
          beforeDiv =`<video width="100%" height="100%" controls> <source src="${beforeSrc}" type="video/mp4"> Your browser does not support the video tag. </video>`;
          
        } else {
          beforeDiv = `<div style="color: black;">${beforeFileName} had been uploaded. </div>`;
          afterDiv = `<div style="color: black;">${beforeFileName} had been encode to ${fileName}. Please press download to view the file</div>`;
        }
      }
      afterEle.innerHTML = afterDiv;
      beforeEle.innerHTML = beforeDiv;
    })
  }
  catch(e){
    alert("Input file is too big or an had error occurred , please try again.")
    // displayResult.classList.remove("content");
    
    var ele = document.getElementById("preview-overlay");
    ele.classList.remove("open-preview");
    // ele.style.display = "none";
  }
  finally{
    
    loader.classList.add("hide");
    displayResult.classList.remove("content");
    downloadBtn.classList.remove("content");
  }
}

function displayOutput(data){
  console.log(data);
  var loader = document.getElementById("loader");
  var displayResult = document.getElementById("displayResult");
  var downloadBtn = document.getElementById("downloadBtn");
  try {
    ele = document.getElementById("decoded-container")
    var fileName = data.fileName;
    var fileExtension = fileName.split(".")[1]  
    if(fileName == "text"){
      let div = `<div style="color: black;">Decoded text : ${data.src}</div>`;
      ele.innerHTML = div;
    }
    else{
      if (fileExtension == "jpg" || fileExtension == 'png'|| fileExtension == 'jpeg') {
        let imgTag = `<img src="${data.src}" alt="" style="max-width: 100%;max-height:100%; height:auto;width:auto;">`;
        ele.innerHTML = imgTag;
      } else if (fileExtension == "mp3" || fileExtension == "wav") {
        var adui = document.createElement("audio");
        adui.controls 
        let audio = `<audio controls><source src="${data.src}" type="audio/mpeg">Your browser does not support the audio element.</audio>`;
        ele.innerHTML = audio;
      } else if (fileExtension == "mp4" || fileExtension == "avi") {
        let video = `<video style="max-width: 100%;max-height:100%; height:auto;width:auto;" controls> <source src="${data.src}" type="video/mp4"> Your browser does not support the video tag. </video>`;
        ele.innerHTML = video;
      } else {
        let div = `<div style="color: black;">${fileName} had been extracted. Please press download to view file in the output file.</div>`;
        ele.innerHTML = div;
      }
    }
  }
  catch (e) {
    alert("An had error occurred , please try again.")
  }
  finally {
    loader.classList.add("hide");
    displayResult.classList.remove("content");
    downloadBtn.classList.remove("content");
  }
}

function blobToBase64(blob){
  return new Promise((resolve, reject) =>{
    try{
      var reader = new FileReader();
      reader.readAsDataURL(blob); 
      reader.onloadend = function() {
        var base64data = reader.result;                
        resolve(base64data)
      }
    }
    catch(e){
      console.log("Error loading the blob")
      reject(e)
    }

  })
  
}

(function() {
  "use strict";
  var path = window.location.pathname;
  var page = path.split("/").pop();
  
  if(page == "processor.html"){
    initProcessor();
    processerFunction();
  }
  else if(page == "index.html"){
    initEncoder();
    encodedOrDecode = "encode"
  }
  else if(page == "decode.html"){
    initDecoder();
    encodedOrDecode = "decode"
  }
  
  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    if (all) {
      select(el, all).forEach(e => e.addEventListener(type, listener))
    } else {
      select(el, all).addEventListener(type, listener)
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Sidebar toggle
   */
  if (select('.toggle-sidebar-btn')) {
    on('click', '.toggle-sidebar-btn', function(e) {
      select('body').classList.toggle('toggle-sidebar')
    })
  }

  /**
   * Search bar toggle
   */
  if (select('.search-bar-toggle')) {
    on('click', '.search-bar-toggle', function(e) {
      select('.search-bar').classList.toggle('search-bar-show')
    })
  }

  let navbarlinks = select('#navbar .scrollto', true)
  const navbarlinksActive = () => {
    let position = window.scrollY + 200
    navbarlinks.forEach(navbarlink => {
      if (!navbarlink.hash) return
      let section = select(navbarlink.hash)
      if (!section) return
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        navbarlink.classList.add('active')
      } else {
        navbarlink.classList.remove('active')
      }
    })
  }
  window.addEventListener('load', navbarlinksActive)
  onscroll(document, navbarlinksActive)

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  // let selectHeader = select('#header')
  // if (selectHeader) {
  //   const headerScrolled = () => {
  //     if (window.scrollY > 100) {
  //       selectHeader.classList.add('header-scrolled')
  //     } else {
  //       selectHeader.classList.remove('header-scrolled')
  //     }
  //   }
  //   window.addEventListener('load', headerScrolled)
  //   onscroll(document, headerScrolled)
  // }

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }
})()
