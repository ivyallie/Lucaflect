let upload_queue = [];
let user_files = document.getElementById('files');
let preview_image_picker = document.getElementById('preview_image_filepicker')


    let remove_preview = function() {
        let img = document.getElementById('preview_image');
        img.setAttribute('src', '')
    };


    let add_to_file_list = function (file,queued) {
      let file_list = document.getElementById('file_list');
      let file_template = document.getElementById('listed_file_template');
      let clone = file_template.content.cloneNode(true);
      let clone_head = clone.querySelector('li');
      let clone_display_text = clone.querySelector('span.display_text');
      clone_display_text.innerHTML = file.name;
      console.log(upload_queue);
      if (queued) {
       clone_head.classList.add("upload_pending");
      } else {console.log('file is not in queue')}
      file_list.appendChild(clone);
    };



    let invoke_file_picker = function () {
     user_files.click();
    };

    let send_files_to_list = function () {
     let files=user_files.files;
     for (i=0; i<files.length; i++) {
      let file = files[i];
       upload_queue.push(file);
       add_to_file_list(file,true);
     }
     sendFiles();
    };

    let remove_from_upload_queue = function(file) {
     let file_index = upload_queue.indexOf(file);
     if (file_index > -1) {
      upload_queue.splice(file_index,1);
     }
     console.log(upload_queue)
    };


    let update_file_list = function (filename, imgurl) {
     let file_list = document.getElementById('file_list');
     let list_elements = file_list.querySelectorAll('li');
     for (i=0; i<list_elements.length; i++) {
      let listed_name = list_elements[i].querySelector('span.display_text').innerHTML;
      if (listed_name === filename) {
       list_elements[i].classList.remove('upload_pending');
       list_elements[i].setAttribute('data-imgurl', imgurl)
      }
     }
    };

    let send_via_fetch = function (file) {
     let formData = new FormData();
     formData.append('file', file);
     fetch('/upload', {
      method: 'PUT',
      body: formData

     })
             .then(response => response.json())
             .then(result => {
              remove_from_upload_queue(file);
              update_file_list(result['filename'], result['path'])
             })
             .catch(error => {
              console.log('Error:', error);
             })
    };


    let sendFiles = function() {

        for (var i=0; i<upload_queue.length; i++) {
           send_via_fetch(upload_queue[i]);
        };
    };

    let choose_new_preview = function() {
        preview_image_picker.click()
    };

    let upload_preview_image = function() {
      let file = preview_image_picker.files[0];
      let formData = new FormData();
      formData.append('file',file);
      fetch('/upload',{
          method: 'PUT',
          body: formData
      })
          .then(response => response.json())
          .then(result => {
              set_preview_image(result['internal_filename'])
          })
          .catch(error=> {
              console.log('Error:',error);
          })
    };



    let set_preview_image = function(file) {
        let img = document.getElementById('preview_image');
        let img_path = '/uploads/'+file;
        img.setAttribute('src', img_path);
    };


    user_files.addEventListener("change", send_files_to_list);
    document.getElementById('add-images').addEventListener("click", invoke_file_picker);
    preview_image_picker.addEventListener("change", upload_preview_image);