import Offcanvas from 'react-bootstrap/Offcanvas';
import Markdown from 'react-markdown';

import { useAppStateContext } from '../services/appProvider';
import { useQuestionContext } from '../services/questionProvider';
import Reference from './Reference';

function ReferenceOverlay() {
    const { showRefs, setShowRefs } = useAppStateContext();
    const { selectedQuestion } = useQuestionContext();

    const handleClose = () => setShowRefs(false);

    return (
        <Offcanvas show={showRefs} placement='end' onHide={handleClose}>
            <Offcanvas.Header closeButton>
                <Offcanvas.Title>References</Offcanvas.Title>
            </Offcanvas.Header>
            <Offcanvas.Body>
                {selectedQuestion && selectedQuestion.references.length > 0 ? (
                    selectedQuestion.article.map((section) => (
                        <div style={{paddingTop: "20px", paddingLeft: "20px", paddingBottom:"10px"}}>
                            <Markdown>{section.header}</Markdown>
                            {section.references.map((i_ref) => (
                                <Reference
                                    type={selectedQuestion.references[i_ref].type}
                                    name={selectedQuestion.references[i_ref].name}
                                    link={selectedQuestion.references[i_ref].link}
                                />
                            ))}
                        </div>
                    ))
                ) : (
                    <p>No references used</p>
                )}
            </Offcanvas.Body>
        </Offcanvas>
    );
}

export default ReferenceOverlay;
