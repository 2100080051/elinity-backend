from fastapi import APIRouter, Depends, HTTPException, status
from utils.token import get_current_user
from models.user import Tenant
from schemas.multimodal import MultimodalSchema,MultimodalResponse
from database.session import get_db, Session
from elinity_ai.multimodal import ElinityMultimodal
from elinity_ai.smart_journal import ElinitySmartJournal

router = APIRouter()

transcript = ElinityMultimodal()
smart_journal = ElinitySmartJournal()

@router.post("/process/", tags=["Multimodal"], response_model=MultimodalResponse)
async def process(request: MultimodalSchema, current_user: Tenant = Depends(get_current_user),db: Session = Depends(get_db)) -> dict:
    try:
        # result = transcript.process(request.url)
        result = "Runner's Knee Runner's knee is a condition characterized by pain behind or around the kneecap. It is caused by overuse, muscle imbalance and inadequate stretching. Symptoms include pain under or around the kneecap, pain when walking sprained ankle 1 nil here in the 37th minute she is between two Guatemalan defenders and then goes down and stays down and you will see why. The ligaments of the ankle holds the ankle bones and joint in position. They protect the ankle from abnormal movements such as twisting, turning and rolling of the foot. A sprained ankle happens when the foot twists, rolls or turns beyond its normal motions. If the force is too strong, the ligaments can tear. Symptoms include pain and difficulty moving the ankle, swelling around the ankle and bruising. Meniscus tear and I think some of it was just being scared, but this guy, he act like he want to go after Patrick each of your knees has two menisci c shaped pieces of cartilage that act like a cushion between your shin bone and your thigh bone. A meniscus tear happens when you forcibly twist or rotate your knee, especially when putting the pressure of your full weight on it, leading to a torn meniscus. Symptoms include stiffness and swelling, pain in your knee, catching or locking of your knee. Rotator Cuff TEAR Cuff Kobe Traveling to Los Angeles today to be examined by team doctors on the rotator cuff attaches the humerus to the shoulder blade and helps to lift and rotate your arm. A rotator cuff tear is caused by a fall onto your arm or if you lift a heavy object too fast, the tendon can partially or completely tear off of the humerus. Head Symptoms include pain when lifting and lowering your arm, weakness when lifting or rotating your arm, pain when lying on the affected shoulder. ACL tear here's Rosario on the break now and watch Nerlens go up with a left hand, block the shot and then on landing, there came the the ACL runs diagonally in the middle of the knee and provides stability. Anterior cruciate ligament tear occurs when your foot is firmly planted on the ground and a sudden force hits your knee while your leg is straight or slightly bent. This can happen when you are changing direction, rapidly slowing down. When running or landing from a jump, the ligament completely tears into two pieces, making the knee unstable. Symptoms include severe pain and tenderness in knee, loss of full range of motion, swelling around the knee."
        insights = smart_journal.generate_insights(result)
        return MultimodalResponse(url=request.url,text=result,insights=insights)
    except Exception as e:
        logger.error(f"Error processing multimodal: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
