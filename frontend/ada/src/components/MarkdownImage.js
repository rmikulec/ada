import Markdown from "react-markdown";

function MarkdownImage({image, markdown}) {

  return (
    <div className='markdown-image'>
        <img 
            src={image}
            alt="new"
            style={{ width: '50vw', height: '50vh', objectFit: 'cover' }}
        />
        <Markdown>{markdown}</Markdown>
    </div>
  );
}

export default MarkdownImage;