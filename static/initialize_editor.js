let initialize_editor = function(content) {
    console.log('Initializing editor');
    let title = document.getElementById('title');
    let body = document.getElementById('body');
    let tags = document.getElementById('tags');
    let infinitecanvas = document.getElementById('infinitecanvas');
    let post_button = document.getElementById('post-button');

    title.value = content['title'];
    body.value = content['body'];
    tags.value = content['tags'].toString();
    let format = content['format'];
    if (format === 'infinite_canvas') {
        infinitecanvas.checked()
    }
    for (i=0; i<content['imagelist'].length; i++) {
        let image = content['imagelist'][i];
        let image_name = image['file_shortname'];
        let image_url = image['file_path'];
        populate_file_list(image_name,image_url)
    }

    let id = content['id'].toString();
    console.log('Comic id:',id);
    post_button.setAttribute('data-id',id);
    post_button.value = 'Update';
};

let populate_file_list = function(display_name,real_name) {
    console.log(real_name);
    let file_list = document.getElementById('file_list');
    let file_template = document.getElementById('listed_file_template');
      let clone = file_template.content.cloneNode(true);
      let clone_head = clone.querySelector('li');
      let clone_display_text = clone.querySelector('span.display_text');
      clone_display_text.innerHTML = display_name;
      clone_head.setAttribute('data-imgurl',real_name);
    file_list.appendChild(clone)
};