// --- CONFIGURATION ---
const PLAYLIST = [
        'assets/Viking_Berserker_Rage_Cinematic_Video (1).mp4', 
        'assets/Viking_Berserker_Rage_Cinematic_Video (2).mp4',
        'assets/Viking_Berserker_Rage_Cinematic_Video (3).mp4',
        'assets/Viking_Berserker_Rage_Cinematic_Video (4).mp4',
        'assets/Viking_Berserker_Rage_Cinematic_Video (5).mp4'
];

const FADE_DURATION = 1400; // 2 seconds

// --- STATE & DOM ELEMENTS ---
const player1 = document.getElementById('v1');
const player2 = document.getElementById('v2');
const statusDisplay = document.getElementById('status-display');

// 1 = Player 1 is active/visible
// 2 = Player 2 is active/visible
let activePlayerId = 1; 

// Index of the video CURRENTLY visible
let currentPlaylistIndex = 0; 

// Prevent multiple fades triggering at once
let isTransitioning = false;

// --- HELPER FUNCTIONS ---

function getNextIndex(idx) {
    // Modulo operator (%) ensures it wraps from 4 back to 0
    return (idx + 1) % PLAYLIST.length;
}

function getActivePlayer() {
    return activePlayerId === 1 ? player1 : player2;
}

function getHiddenPlayer() {
    return activePlayerId === 1 ? player2 : player1;
}

// --- MAIN ENGINE ---

function init() {
    if (PLAYLIST.length === 0) return;

    // Setup initial state
    player1.src = PLAYLIST[0];
    player1.load();

    // Preload the next video in the background player
    player2.src = PLAYLIST[1];
    player2.load();

    // Attempt to play the first video
    player1.play().then(() => {
        player1.classList.add('visible');
        statusDisplay.textContent = "Loop Cycle Active";
    }).catch(err => {
        console.warn("Autoplay blocked:", err);
        statusDisplay.textContent = "Click to Initialize";
        // Add a global click listener to start if autoplay is blocked
        document.body.addEventListener('click', () => {
            player1.play();
            player1.classList.add('visible');
        }, { once: true });
    });
}

function performCrossfade() {
    isTransitioning = true;

    const currentVid = getActivePlayer();
    const nextVid = getHiddenPlayer();
    const nextIdx = getNextIndex(currentPlaylistIndex);

    console.log(`Fading to Index: ${nextIdx} (${PLAYLIST[nextIdx]})`);

    // 1. Play the preloaded 'next' video
    nextVid.play().then(() => {
        
        // 2. Visually swap them
        nextVid.classList.add('visible');
        currentVid.classList.remove('visible');

        // 3. Wait for the CSS transition (fade) to complete
        setTimeout(() => {
            // --- SWAP LOGIC ---
            
            // Stop the old video to save CPU
            currentVid.pause();
            currentVid.currentTime = 0;

            // Update State
            activePlayerId = activePlayerId === 1 ? 2 : 1;
            currentPlaylistIndex = nextIdx;
            
            // --- PRELOAD THE NEXT STEP ---
            // Calculate what comes AFTER the video we just switched to
            const futureIndex = getNextIndex(currentPlaylistIndex);
            
            // Load that future video into the NOW hidden player
            currentVid.src = PLAYLIST[futureIndex];
            currentVid.load();
            
            isTransitioning = false;
            
        }, FADE_DURATION);

    }).catch(e => {
        console.error("Error playing next video:", e);
        isTransitioning = false;
    });
}

function checkTime(e) {
    // Only the currently active player should trigger the check
    const player = e.target;
    
    // Safety check: ignore events from the hidden/buffering player
    if (player !== getActivePlayer()) return;

    const remainingTime = player.duration - player.currentTime;

    // Trigger fade if we are within the fade window (2s) and not already fading
    // 'remainingTime > 0.1' prevents double triggers at the exact end
    if (remainingTime < (FADE_DURATION / 1000) && remainingTime > 0.1 && !isTransitioning) {
        performCrossfade();
    }
}

// --- EVENT LISTENERS ---
player1.addEventListener('timeupdate', checkTime);
player2.addEventListener('timeupdate', checkTime);

// --- START ---
document.addEventListener('DOMContentLoaded', init);