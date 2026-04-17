// Skills tag input — only runs if the skills section is present (Participant role)
const skillsInput  = document.getElementById('skillsInput');
const skillsTags   = document.getElementById('skillsTags');
const skillsHidden = document.getElementById('skillsHidden');
const skillsWrap   = document.getElementById('skillsWrap');
let skills = [];

function syncCheckboxes() {
    document.querySelectorAll('.qp-chip input[type="checkbox"]').forEach(cb => {
        cb.checked = skills.includes(cb.value);
    });
}

function renderTags() {
    if (!skillsTags) return;
    skillsTags.innerHTML = '';
    skills.forEach((skill, i) => {
        const tag = document.createElement('span');
        tag.className = 'skill-tag';
        tag.innerHTML = `${skill} <button type="button" aria-label="Remove ${skill}">&times;</button>`;
        tag.querySelector('button').addEventListener('click', () => {
            skills.splice(i, 1);
            syncCheckboxes();
            renderTags();
        });
        skillsTags.appendChild(tag);
    });
    if (skillsHidden) {
        skillsHidden.value = skills.join(',');
    }
}

if (skillsInput) {
    skillsWrap.addEventListener('click', () => skillsInput.focus());

    skillsInput.addEventListener('keydown', e => {
        if ((e.key === 'Enter' || e.key === ',') && skillsInput.value.trim()) {
            e.preventDefault();
            const val = skillsInput.value.trim().replace(/,$/, '');
            if (val && !skills.includes(val) && skills.length < 10) {
                skills.push(val);
                renderTags();
            }
            skillsInput.value = '';
        }
        if (e.key === 'Backspace' && !skillsInput.value && skills.length) {
            skills.pop();
            syncCheckboxes();
            renderTags();
        }
    });
}

// Quick-pick checkboxes sync with tag list
document.querySelectorAll('.qp-chip input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', () => {
        const val = cb.value;
        if (cb.checked) {
            if (!skills.includes(val) && skills.length < 10) {
                skills.push(val);
            } else {
                cb.checked = false; // cap at 10
            }
        } else {
            skills = skills.filter(s => s !== val);
        }
        renderTags();
    });
});

// Cursor glow
document.addEventListener("mousemove", e => {
    document.documentElement.style.setProperty("--mx", e.clientX + "px");
    document.documentElement.style.setProperty("--my", e.clientY + "px");
});
