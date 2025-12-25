"""
Comprehensive Urgent Care Medical Knowledge Base
Based on official sources: CDC, Mayo Clinic, American Red Cross, WHO
"""

URGENT_CARE_KNOWLEDGE = {
    # ==================== EMERGENCY CONDITIONS ====================
    "heart_attack": {
        "category": "emergency",
        "term": "Heart Attack (Myocardial Infarction)",
        "triage_level": "EMERGENCY",
        "description": "Blockage of blood flow to the heart muscle, requiring immediate medical attention",
        "symptoms": [
            "Chest pain or pressure (crushing, squeezing sensation)",
            "Pain radiating to arm, jaw, neck, or back",
            "Shortness of breath",
            "Cold sweats",
            "Nausea or vomiting",
            "Lightheadedness or sudden dizziness"
        ],
        "assessment_questions": [
            "Are you experiencing chest pain or pressure?",
            "Is the pain spreading to your arm, jaw, or back?",
            "Are you having difficulty breathing?",
            "Are you experiencing cold sweats or nausea?"
        ],
        "immediate_action": "🚨 CALL 911 IMMEDIATELY - DO NOT DRIVE YOURSELF",
        "first_aid": [
            "Call 911 immediately - time is critical",
            "Have the person sit down and rest",
            "If they have prescribed nitroglycerin, help them take it",
            "If the person is not allergic to aspirin, have them chew one adult aspirin (325mg)",
            "Loosen any tight clothing",
            "Stay with the person until emergency help arrives",
            "If they become unconscious and stops breathing, begin CPR if trained"
        ],
        "do_not": [
            "Do NOT let the person convince you to wait or 'see if it passes'",
            "Do NOT drive yourself - always call 911",
            "Do NOT delay calling for help",
            "Do NOT give them anything to eat or drink except prescribed medication"
        ],
        "red_flags": [
            "Loss of consciousness",
            "Stopped breathing",
            "No pulse",
            "Severe chest pain lasting more than a few minutes"
        ],
        "source": "American Heart Association",
        "source_url": "https://www.heart.org/en/health-topics/heart-attack/warning-signs-of-a-heart-attack"
    },
    
    "stroke": {
        "category": "emergency",
        "term": "Stroke (Brain Attack)",
        "triage_level": "EMERGENCY",
        "description": "Interrupted blood flow to the brain, causing brain cell damage",
        "symptoms": [
            "Sudden numbness or weakness in face, arm, or leg (especially one side)",
            "Sudden confusion or trouble speaking",
            "Sudden trouble seeing in one or both eyes",
            "Sudden trouble walking, dizziness, loss of balance",
            "Sudden severe headache with no known cause"
        ],
        "assessment_questions": [
            "F.A.S.T. Test:",
            "Face: Ask them to smile - does one side droop?",
            "Arms: Ask them to raise both arms - does one drift downward?",
            "Speech: Ask them to repeat a simple phrase - is speech slurred?",
            "Time: If any symptoms present, call 911 immediately"
        ],
        "immediate_action": "🚨 CALL 911 IMMEDIATELY - EVERY MINUTE COUNTS",
        "first_aid": [
            "Call 911 immediately - note the time symptoms started",
            "Keep the person calm and lying down with head slightly elevated",
            "Do NOT give them anything to eat or drink",
            "If unconscious, turn them on their side (recovery position)",
            "Monitor breathing and be prepared to perform CPR if needed",
            "Note all symptoms and when they started for emergency responders"
        ],
        "do_not": [
            "Do NOT wait to see if symptoms improve",
            "Do NOT give aspirin or other medication - let emergency responders decide",
            "Do NOT let them eat or drink anything"
        ],
        "red_flags": [
            "Any F.A.S.T. test failure",
            "Sudden severe headache",
            "Loss of consciousness",
            "Difficulty breathing"
        ],
        "source": "American Stroke Association",
        "source_url": "https://www.stroke.org/en/about-stroke/stroke-symptoms"
    },
    
    "anaphylaxis": {
        "category": "emergency",
        "term": "Severe Allergic Reaction (Anaphylaxis)",
        "triage_level": "EMERGENCY",
        "description": "Life-threatening allergic reaction requiring immediate epinephrine and emergency care",
        "symptoms": [
            "Difficulty breathing or wheezing",
            "Swelling of lips, tongue, or throat",
            "Rapid or weak pulse",
            "Skin rash, hives, or itching",
            "Nausea, vomiting, or diarrhea",
            "Dizziness or fainting",
            "Feeling of impending doom"
        ],
        "assessment_questions": [
            "Are you having difficulty breathing or swallowing?",
            "Is your throat or tongue swelling?",
            "Do you have an EpiPen or epinephrine auto-injector?",
            "Are you experiencing hives, rash, or severe itching?"
        ],
        "immediate_action": "🚨 CALL 911 AND USE EPIPEN IF AVAILABLE",
        "first_aid": [
            "Call 911 immediately",
            "If the person has an epinephrine auto-injector (EpiPen), help them use it immediately",
            "Have them lie flat and elevate their legs (unless having trouble breathing)",
            "If having trouble breathing, help them sit up",
            "Do NOT give them anything to drink",
            "Be prepared to perform CPR if they stop breathing",
            "If symptoms don't improve in 5-15 minutes, give second dose of epinephrine if available"
        ],
        "do_not": [
            "Do NOT wait to see if symptoms improve",
            "Do NOT assume antihistamines alone will be enough",
            "Do NOT have them stand up abruptly"
        ],
        "red_flags": [
            "Difficulty breathing",
            "Swelling of throat or tongue",
            "Loss of consciousness",
            "Rapid progression of symptoms"
        ],
        "source": "American Academy of Allergy, Asthma & Immunology",
        "source_url": "https://www.aaaai.org/conditions-and-treatments/library/allergy-library/anaphylaxis"
    },
    
    "severe_bleeding": {
        "category": "emergency",
        "term": "Severe Bleeding (Hemorrhage)",
        "triage_level": "EMERGENCY",
        "description": "Heavy bleeding that won't stop with direct pressure",
        "symptoms": [
            "Blood soaking through bandages",
            "Spurting or pulsing blood",
            "Blood pooling on the ground",
            "Weakness, confusion, or loss of consciousness",
            "Pale, cool, clammy skin"
        ],
        "assessment_questions": [
            "How much blood have you lost?",
            "Is the bleeding spurting or continuous?",
            "Can you control it with direct pressure?",
            "Are you feeling weak or dizzy?"
        ],
        "immediate_action": "🚨 CALL 911 WHILE APPLYING DIRECT PRESSURE",
        "first_aid": [
            "Call 911 immediately",
            "Apply direct pressure to the wound with a clean cloth or bandage",
            "If blood soaks through, add more bandages on top - don't remove the first one",
            "If possible, elevate the injured area above the heart",
            "For severe limb bleeding, apply pressure to pressure points",
            "Keep the person warm with a blanket",
            "Have them lie down to prevent shock",
            "Do NOT remove embedded objects - stabilize them instead"
        ],
        "do_not": [
            "Do NOT remove deeply embedded objects",
            "Do NOT peek at the wound - maintain constant pressure",
            "Do NOT use a tourniquet unless trained and bleeding is life-threatening"
        ],
        "red_flags": [
            "Blood spurting from wound",
            "Bleeding that won't stop after 10 minutes of direct pressure",
            "Signs of shock (pale skin, rapid pulse, confusion)",
            "Large amount of blood loss"
        ],
        "source": "American Red Cross",
        "source_url": "https://www.redcross.org/take-a-class/cpr/performing-cpr/cpr-steps"
    },

    "difficulty_breathing": {
        "category": "emergency",
        "term": "Severe Difficulty Breathing",
        "triage_level": "EMERGENCY",
        "description": "Severe shortness of breath requiring immediate medical attention",
        "symptoms": [
            "Cannot speak in full sentences",
            "Gasping for air",
            "Blue lips or fingernails",
            "Chest pain with breathing",
            "Rapid breathing",
            "Confusion or altered mental state"
        ],
        "assessment_questions": [
            "Can you speak in full sentences?",
            "Are your lips or fingernails turning blue?",
            "Do you have a history of asthma or COPD?",
            "Did this start suddenly?"
        ],
        "immediate_action": "🚨 CALL 911 IMMEDIATELY",
        "first_aid": [
            "Call 911 immediately",
            "Help the person sit upright (easier to breathe)",
            "Loosen any tight clothing around neck and chest",
            "If they have a rescue inhaler, help them use it",
            "Keep them calm - panic makes breathing worse",
            "Open windows for fresh air if indoors",
            "Monitor their breathing and be ready to perform CPR if breathing stops"
        ],
        "do_not": [
            "Do NOT have them lie flat",
            "Do NOT leave them alone",
            "Do NOT give them anything to eat or drink"
        ],
        "red_flags": [
            "Blue or gray skin color",
            "Loss of consciousness",
            "Stopped breathing",
            "Severe chest pain"
        ],
        "source": "Mayo Clinic",
        "source_url": "https://www.mayoclinic.org/symptoms/shortness-of-breath/basics/when-to-see-doctor/sym-20050890"
    },

    # ==================== URGENT CONDITIONS ====================
    
    "second_degree_burn": {
        "category": "urgent",
        "term": "Second-Degree Burn",
        "triage_level": "URGENT",
        "description": "Burn affecting outer and underlying layer of skin, with blisters",
        "symptoms": [
            "Red, swollen, blistered skin",
            "Severe pain",
            "Possible oozing or weeping of fluid",
            "Burn larger than 3 inches (7.5 cm)",
            "Burn on face, hands, feet, genitals, or major joints"
        ],
        "assessment_questions": [
            "How large is the burned area?",
            "Where on your body is the burn?",
            "Are there blisters?",
            "How did the burn happen?",
            "When did it occur?"
        ],
        "immediate_action": "Seek medical care immediately if burn is large or on sensitive areas",
        "first_aid": [
            "Remove from heat source immediately",
            "Cool the burn with cool (not ice-cold) running water for 10-20 minutes",
            "Do NOT use ice - it can cause further damage",
            "Do NOT break blisters - they protect against infection",
            "Remove jewelry and tight clothing before swelling starts",
            "Cover burn loosely with sterile, non-stick bandage or clean cloth",
            "Do NOT apply butter, oil, or ointments",
            "Take over-the-counter pain reliever (ibuprofen or acetaminophen)",
            "Keep the burn elevated if possible to reduce swelling"
        ],
        "when_to_seek_care": [
            "Immediately if burn is larger than 3 inches (7.5 cm)",
            "If burn is on face, hands, feet, genitals, or major joints",
            "If blisters are large or breaking",
            "Within 24 hours for all second-degree burns",
            "If signs of infection develop (increased pain, redness, swelling, pus, fever)"
        ],
        "red_flags": [
            "Burn covers large area",
            "Burn looks white, black, or charred (third-degree)",
            "Fever develops",
            "Increased pain, redness, or pus (infection)",
            "Burn on face, hands, feet, or genitals"
        ],
        "self_care": [
            "Keep burn clean and dry",
            "Change bandages daily",
            "Watch for signs of infection",
            "Avoid sun exposure on healing burn for at least a year"
        ],
        "source": "American Burn Association / Mayo Clinic",
        "source_url": "https://www.mayoclinic.org/first-aid/first-aid-burns/basics/art-20056649"
    },

    "high_fever_children": {
        "category": "urgent",
        "term": "High Fever in Children",
        "triage_level": "URGENT",
        "description": "Temperature above 104°F (40°C) in children requiring medical evaluation",
        "symptoms": [
            "Temperature 104°F (40°C) or higher",
            "Fever lasting more than 3 days",
            "Fever in infant under 3 months (any fever)",
            "Irritability or lethargy",
            "Difficulty breathing",
            "Rash",
            "Severe headache",
            "Stiff neck"
        ],
        "assessment_questions": [
            "What is the child's temperature?",
            "How old is the child?",
            "How long has the fever lasted?",
            "Are there other symptoms (rash, vomiting, difficulty breathing)?",
            "Is the child drinking fluids?",
            "Is the child responsive and alert?"
        ],
        "immediate_action": "Seek medical care within 2-4 hours",
        "first_aid": [
            "Give age-appropriate fever reducer (acetaminophen or ibuprofen - NOT aspirin)",
            "Follow dosage instructions carefully based on weight",
            "Dress child in light clothing",
            "Keep room temperature comfortable (68-70°F)",
            "Offer plenty of fluids (water, clear broth, popsicles)",
            "Give lukewarm bath (NOT cold) if fever is very high",
            "Monitor temperature every 2-3 hours",
            "Watch for signs of dehydration (dry mouth, no tears, decreased urination)"
        ],
        "when_to_seek_care": [
            "IMMEDIATELY if infant under 3 months has any fever",
            "Within 2 hours if fever is 104°F (40°C) or higher",
            "Within 24 hours if fever lasts more than 3 days",
            "Immediately if child has seizure, severe headache, or stiff neck"
        ],
        "red_flags": [
            "Infant under 3 months with any fever",
            "Fever with rash that doesn't fade when pressed",
            "Seizures",
            "Difficulty breathing",
            "Severe headache or stiff neck",
            "Extreme lethargy or won't wake",
            "Inconsolable crying"
        ],
        "self_care": [
            "Rest is important",
            "Keep child hydrated",
            "Monitor temperature regularly",
            "Watch for worsening symptoms"
        ],
        "source": "CDC / American Academy of Pediatrics",
        "source_url": "https://www.cdc.gov/ncbddd/childdevelopment/features/medications-for-fever.html"
    },

    "suspected_fracture": {
        "category": "urgent",
        "term": "Suspected Fracture (Broken Bone)",
        "triage_level": "URGENT",
        "description": "Possible broken bone requiring medical imaging and treatment",
        "symptoms": [
            "Severe pain at injury site",
            "Visible deformity or abnormal angle",
            "Swelling and bruising",
            "Inability to move or bear weight",
            "Bone protruding through skin (compound fracture - EMERGENCY)",
            "Grinding or popping sound at time of injury"
        ],
        "assessment_questions": [
            "Where does it hurt?",
            "Can you move the injured area?",
            "Is there visible deformity?",
            "Did you hear a crack or pop?",
            "Can you bear weight on it (if leg/foot)?"
        ],
        "immediate_action": "Seek medical care within 4-6 hours (IMMEDIATE if bone protruding)",
        "first_aid": [
            "Do NOT try to straighten or realign the bone",
            "Do NOT move the injured area",
            "Immobilize the injury in the position found",
            "Apply ice pack wrapped in cloth (20 minutes on, 20 minutes off)",
            "Elevate if possible to reduce swelling",
            "For arm/wrist: make a sling with cloth or jacket",
            "For leg: use boards, rolled newspapers, or pillows to splint",
            "Give over-the-counter pain medication if not allergic",
            "Call for medical transport if person cannot be moved safely"
        ],
        "when_to_seek_care": [
            "IMMEDIATELY if bone is protruding through skin",
            "IMMEDIATELY if limb is cold, numb, or blue",
            "Within 2-6 hours for suspected fracture",
            "Same day for severe pain or deformity"
        ],
        "red_flags": [
            "Bone protruding through skin",
            "Limb is cold, blue, or numb (circulation problem)",
            "Severe bleeding",
            "Loss of pulse below injury",
            "Fracture of spine, neck, or skull"
        ],
        "self_care": [
            "Keep immobilized until medical care",
            "Ice regularly to reduce swelling",
            "Elevate if possible",
            "Do not eat or drink (may need surgery)"
        ],
        "source": "American Academy of Orthopaedic Surgeons",
        "source_url": "https://orthoinfo.aaos.org/en/diseases--conditions/fractures-broken-bones/"
    },

    # ==================== COMMON/ROUTINE CONDITIONS ====================
    
    "minor_burn": {
        "category": "routine",
        "term": "Minor Burn (First-Degree)",
        "triage_level": "ROUTINE",
        "description": "Superficial burn affecting only outer layer of skin",
        "symptoms": [
            "Red skin without blisters",
            "Pain and tenderness",
            "Minor swelling",
            "Burn smaller than 3 inches"
        ],
        "assessment_questions": [
            "How large is the burn?",
            "Are there any blisters?",
            "Where is the burn located?",
            "How did it happen?"
        ],
        "immediate_action": "Can be treated at home with first aid",
        "first_aid": [
            "Cool the burn immediately with cool (not ice-cold) running water for 10-15 minutes",
            "Remove jewelry or tight items before swelling begins",
            "Do NOT use ice - it can cause further damage",
            "Do NOT apply butter, oils, or ointments initially",
            "After cooling, gently pat dry with clean cloth",
            "Apply aloe vera gel or over-the-counter burn cream",
            "Cover loosely with sterile gauze bandage",
            "Take over-the-counter pain reliever (ibuprofen or acetaminophen) if needed",
            "Keep burn clean and protected"
        ],
        "when_to_seek_care": [
            "If burn doesn't improve in a few days",
            "If signs of infection develop (increased redness, pus, fever)",
            "If pain worsens instead of improves",
            "If unsure about severity"
        ],
        "red_flags": [
            "Blisters forming",
            "Burn larger than 3 inches",
            "Increased pain, redness, or swelling after 24 hours",
            "Fever",
            "Pus or drainage"
        ],
        "self_care": [
            "Change bandage daily or when wet",
            "Keep clean and dry",
            "Apply aloe vera or burn cream 2-3 times daily",
            "Protect from sun exposure during healing",
            "Watch for signs of infection"
        ],
        "source": "American Red Cross / Mayo Clinic",
        "source_url": "https://www.mayoclinic.org/first-aid/first-aid-burns/basics/art-20056649"
    },

    "minor_cuts": {
        "category": "routine",
        "term": "Minor Cuts and Scrapes",
        "triage_level": "ROUTINE",
        "description": "Superficial skin injury that can be treated at home",
        "symptoms": [
            "Shallow cut or scrape",
            "Bleeding that stops with pressure",
            "Clean wound edges",
            "No embedded objects"
        ],
        "assessment_questions": [
            "How deep is the cut?",
            "Is the bleeding controlled?",
            "Is the wound clean?",
            "When was your last tetanus shot?"
        ],
        "immediate_action": "Can be treated at home",
        "first_aid": [
            "Wash your hands thoroughly with soap and water",
            "Stop bleeding by applying gentle pressure with clean cloth (5-10 minutes)",
            "Clean the wound with cool running water",
            "Gently remove dirt or debris with tweezers cleaned with alcohol",
            "Apply antibiotic ointment (Neosporin, Bacitracin)",
            "Cover with adhesive bandage or sterile gauze",
            "Change bandage daily or when wet/dirty",
            "Watch for signs of infection"
        ],
        "when_to_seek_care": [
            "If wound is deep or gaping (may need stitches)",
            "If bleeding doesn't stop after 10 minutes of pressure",
            "If caused by rusty or dirty object and tetanus shot not current",
            "If signs of infection develop (redness, warmth, pus, fever)",
            "If wound is from animal or human bite"
        ],
        "red_flags": [
            "Bleeding that won't stop",
            "Deep cut with visible fat or muscle",
            "Cut wider than 1/4 inch or gaping open",
            "Numbness or loss of function",
            "Signs of infection after 24-48 hours"
        ],
        "self_care": [
            "Keep wound clean and dry",
            "Change bandage daily",
            "Apply antibiotic ointment",
            "Watch for signs of infection",
            "Tetanus booster if last shot was more than 5 years ago (for dirty wounds)"
        ],
        "source": "American Academy of Family Physicians",
        "source_url": "https://familydoctor.org/condition/cuts-scrapes-and-stitches/"
    },

    "sprain": {
        "category": "routine",
        "term": "Sprain or Strain",
        "triage_level": "ROUTINE",
        "description": "Stretched or torn ligament (sprain) or muscle/tendon (strain)",
        "symptoms": [
            "Pain at injury site",
            "Swelling and bruising",
            "Limited range of motion",
            "Difficulty bearing weight (if leg/ankle)",
            "Muscle spasm"
        ],
        "assessment_questions": [
            "How did the injury occur?",
            "Can you move the joint?",
            "Can you bear weight on it?",
            "Is there severe swelling or deformity?"
        ],
        "immediate_action": "Use R.I.C.E. method at home",
        "first_aid": [
            "R.I.C.E. Method:",
            "R - Rest: Avoid using injured area for 24-48 hours",
            "I - Ice: Apply ice pack wrapped in towel for 20 minutes every 2-3 hours",
            "C - Compression: Wrap with elastic bandage (not too tight)",
            "E - Elevation: Raise above heart level to reduce swelling",
            "",
            "Additional care:",
            "Take over-the-counter pain reliever (ibuprofen or acetaminophen)",
            "Do NOT apply heat for first 48 hours",
            "Gentle movement after 48 hours to prevent stiffness",
            "Use crutches if walking is painful (ankle/knee)"
        ],
        "when_to_seek_care": [
            "If pain and swelling don't improve after 2-3 days",
            "If you can't bear any weight on the limb",
            "If joint feels unstable or gives out",
            "If severe pain, deformity, or numbness present",
            "If no improvement after 1 week of home care"
        ],
        "red_flags": [
            "Severe pain or inability to move joint",
            "Obvious deformity",
            "Numbness or tingling",
            "Joint feels unstable",
            "Severe swelling or bruising",
            "No improvement after 48 hours"
        ],
        "self_care": [
            "Continue R.I.C.E. for 48-72 hours",
            "After 48 hours, gentle stretching and movement",
            "Gradual return to normal activities",
            "Strengthen muscles around joint once healed"
        ],
        "source": "American Academy of Orthopaedic Surgeons",
        "source_url": "https://orthoinfo.aaos.org/en/diseases--conditions/sprains-and-strains-whats-the-difference/"
    },

    "mild_fever": {
        "category": "routine",
        "term": "Mild to Moderate Fever (Adults)",
        "triage_level": "ROUTINE",
        "description": "Temperature between 100-102°F (37.8-39°C) in adults",
        "symptoms": [
            "Temperature 100-102°F (37.8-39°C)",
            "Feeling warm",
            "Mild sweating",
            "General discomfort",
            "Other cold/flu symptoms"
        ],
        "assessment_questions": [
            "What is your temperature?",
            "How long have you had the fever?",
            "Do you have other symptoms (cough, sore throat, body aches)?",
            "Have you been exposed to anyone sick?"
        ],
        "immediate_action": "Rest and home care usually sufficient",
        "first_aid": [
            "Get plenty of rest",
            "Drink lots of fluids (water, herbal tea, clear broth)",
            "Take fever reducer: acetaminophen (Tylenol) or ibuprofen (Advil, Motrin)",
            "Follow package dosing instructions",
            "Dress in light, breathable clothing",
            "Keep room temperature comfortable",
            "Take lukewarm bath or shower if feeling very warm",
            "Use cool, damp washcloth on forehead",
            "Eat light, easy-to-digest foods when hungry"
        ],
        "when_to_seek_care": [
            "If fever lasts more than 3 days",
            "If fever goes above 103°F (39.4°C)",
            "If accompanied by severe headache, stiff neck, or rash",
            "If difficulty breathing or chest pain develops",
            "If severe abdominal pain or vomiting occurs",
            "If you have underlying health conditions"
        ],
        "red_flags": [
            "Fever above 103°F (39.4°C)",
            "Fever lasting more than 3 days",
            "Severe headache with stiff neck",
            "Difficulty breathing",
            "Chest pain",
            "Confusion or difficulty staying awake",
            "Rash that doesn't fade when pressed"
        ],
        "self_care": [
            "Monitor temperature every 4-6 hours",
            "Stay hydrated - aim for pale yellow urine",
            "Rest as much as possible",
            "Avoid alcohol and caffeine",
            "Wash hands frequently to prevent spread"
        ],
        "source": "Mayo Clinic / CDC",
        "source_url": "https://www.mayoclinic.org/diseases-conditions/fever/diagnosis-treatment/drc-20352764"
    }
}

# Add more conditions as needed...
