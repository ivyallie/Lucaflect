let postComic = function () {
    let title = document.getElementById('title').value;
    let bodytext = document.getElementById('body').value;
    let tags = document.getElementById('tags').value;
    let image_list = getImageList();
    let post = {
        'title' : title,
        'bodytext' : bodytext,
        'tags' : tags.split(','),
        'image_list' : image_list
    };
    let post_json = JSON.stringify(post);
    fetch('/post_comic', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: post_json,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Something went wrong');
            }
            return response.json();
        })
        .then(data => alert('Success.'))
        .catch((error) => { alert('Fail.');})
};

let getImageList = function () {
    console.log('Image list');
    let file_list = document.getElementById('file_list');
    let list_elements = file_list.querySelectorAll('li');
    let image_list = [];
    for (i=0; i<list_elements.length; i++) {
        let file_shortname = list_elements[i].querySelector('span.display_text').innerHTML
        let file_path = list_elements[i].getAttribute('data-imgurl');
        let image_entry = {'file_shortname': file_shortname, 'file_path': file_path}
        image_list.push(image_entry)
    }
    return image_list
};