import Offcanvas from 'react-bootstrap/Offcanvas';

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
                    selectedQuestion.references.map((ref) => (
                        <div style={{paddingTop: "2px", paddingLeft: "20px", paddingBottom:"2px"}}>
                                <Reference
                                    type={ref.type}
                                    name={ref.name}
                                    link={ref.link}
                                />
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
