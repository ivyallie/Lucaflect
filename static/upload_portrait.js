let button = document.getElementById('portrait_button');
let picker = document.getElementById('portrait_filepicker');
let display = document.getElementById('portrait');

let chooseNewPortrait = function() {
    picker.click()
};

let setPortrait = function(filename) {
    let url = '/uploads/'+filename;
    display.setAttribute('src', url)
};

let uploadPortrait = function() {
    let file=picker.files[0];
    console.log(picker.file);
    let formData = new FormData();
     formData.append('file', file);
     fetch('/upload', {
      method: 'PUT',
      body: formData

     })
             .then(response => response.json())
             .then(result => {
                 setPortrait(result['internal_filename']);
              // console.log('Success:', result['path']);
              console.log(result['path']);
             })
             .catch(error => {
              console.log('Error:', error);
             })

};

picker.addEventListener("change", uploadPortrait)