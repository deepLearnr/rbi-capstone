import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { learningApi } from "../services/learningApi";
import "../styles/Profile.css";

function Profile() {
  const navigate = useNavigate();

  const [isEditing, setIsEditing] = useState(false);

  const [profile, setProfile] = useState({
    name: "Demo Employee",
    designation: "Not configured",
    department: "Not configured",
    employeeId: "Not configured",
    email: "Not configured",
    phone: "Not configured",
    branch: "Not configured",
    joiningDate: "Not configured",
  });

  const [editProfile, setEditProfile] = useState(profile);
  const [learningProgress, setLearningProgress] = useState(null);
  const [learningLoading, setLearningLoading] = useState(true);
  const [learningError, setLearningError] = useState("");

  useEffect(() => {
    let isMounted = true;
    learningApi.progress()
      .then((data) => {
        if (isMounted) setLearningProgress(data);
      })
      .catch((error) => {
        if (isMounted) setLearningError(error.message);
      })
      .finally(() => {
        if (isMounted) setLearningLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // ================= EDIT PROFILE =================

  const handleEdit = () => {
    setEditProfile(profile);
    setIsEditing(true);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setEditProfile((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = () => {
    setProfile(editProfile);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditProfile(profile);
    setIsEditing(false);
  };

  return (
    <div className="profile-page">
      {/* ================= PAGE HEADER ================= */}

      <div className="profile-header">
        <h1>👤 My Profile</h1>

        <p>Demo profile only. Employee details are local UI state, not connected to an employee directory or saved account.</p>
      </div>

      {/* ================= PROFILE SUMMARY ================= */}

      <section className="profile-summary-card">
        <div className="profile-summary-content">
          <div className="profile-avatar">👤</div>

          <div className="profile-basic-info">
            <h2>{profile.name}</h2>

            <p>{profile.designation}</p>

            <span>Department: {profile.department}</span>

            <span>Employee ID: {profile.employeeId}</span>
          </div>
        </div>

        <button className="edit-profile-button" onClick={handleEdit}>
          Edit Profile
        </button>
      </section>

      {/* ================= PERSONAL INFORMATION ================= */}

      <section className="profile-section">
        <h2>👤 Personal Information</h2>

        <div className="profile-info-grid">
          <div className="profile-info-card">
            <label>Full Name</label>
            <p>{profile.name}</p>
          </div>

          <div className="profile-info-card">
            <label>Employee ID</label>
            <p>{profile.employeeId}</p>
          </div>

          <div className="profile-info-card">
            <label>Email</label>
            <p>{profile.email}</p>
          </div>

          <div className="profile-info-card">
            <label>Phone</label>
            <p>{profile.phone}</p>
          </div>
        </div>
      </section>

      {/* ================= WORK INFORMATION ================= */}

      <section className="profile-section">
        <h2>🏢 Work Information</h2>

        <div className="profile-info-grid">
          <div className="profile-info-card">
            <label>Department</label>
            <p>{profile.department}</p>
          </div>

          <div className="profile-info-card">
            <label>Designation</label>
            <p>{profile.designation}</p>
          </div>

          <div className="profile-info-card">
            <label>Branch / Office</label>
            <p>{profile.branch}</p>
          </div>

          <div className="profile-info-card">
            <label>Joining Date</label>
            <p>{profile.joiningDate}</p>
          </div>
        </div>
      </section>

      {/* ================= LEARNING SUMMARY ================= */}

      <section className="profile-section">
        <h2>📚 Learning Summary</h2>

        {learningLoading && (
          <p className="profile-status" role="status">Loading learning statistics…</p>
        )}
        {learningError && (
          <p className="profile-status" role="alert">
            Learning statistics could not be loaded: {learningError}. Values are
            withheld until the backend responds successfully.
          </p>
        )}

        <div className="learning-summary-card">
          <div className="learning-summary-stats">
            <div className="learning-stat">
              <span>Modules Completed</span>
              <strong>{learningProgress ? learningProgress.modules_completed : "—"}</strong>
            </div>
            <div className="learning-stat">
              <span>Published Modules</span>
              <strong>{learningProgress ? learningProgress.module_count : "—"}</strong>
            </div>
            <div className="learning-stat">
              <span>Assessment Average</span>
              <strong>
                {learningProgress && learningProgress.attempts_count > 0
                  ? `${learningProgress.assessment_average}%`
                  : "—"}
              </strong>
            </div>
            <div className="learning-stat">
              <span>Assessment Attempts</span>
              <strong>{learningProgress ? learningProgress.attempts_count : "—"}</strong>
            </div>
          </div>

          {learningProgress && (
            <div className="current-learning">
              <h3>Published Module Progress</h3>
              {learningProgress.modules.length > 0 ? (
                learningProgress.modules.map((module) => {
                  const percent = Math.min(
                    100,
                    Math.max(0, Number(module.progress_percent) || 0),
                  );
                  return (
                    <div className="profile-module-progress" key={module.module_id}>
                      <div className="current-learning-name">{module.title}</div>
                      <div className="learning-progress-wrapper">
                        <div
                          className="learning-progress-bar"
                          role="progressbar"
                          aria-label={`${module.title} progress`}
                          aria-valuemin={0}
                          aria-valuemax={100}
                          aria-valuenow={percent}
                        >
                          <div
                            className="learning-progress-fill"
                            style={{ width: `${percent}%` }}
                          />
                        </div>
                        <span>{percent}%</span>
                      </div>
                    </div>
                  );
                })
              ) : (
                <p>No published learning modules are available.</p>
              )}
              <button
                type="button"
                className="continue-learning-button"
                onClick={() => navigate("/learning")}
              >
                Continue Learning →
              </button>
            </div>
          )}
        </div>

        <p className="profile-demo-note">
          Metrics come from the backend progress endpoint and represent one shared
          demo learner because authentication is not implemented. Learning hours
          and certificate totals are not tracked by this prototype.
        </p>
      </section>

      {/* ================= ACHIEVEMENTS ================= */}

      <section className="profile-section">
        <h2>🏆 Achievements</h2>
        <div className="learning-summary-card">
          <div className="current-learning">
            <h3>Achievement tracking is not available</h3>
            <p className="profile-demo-note">
              This prototype does not calculate or persist certificates, badges,
              or learning streaks. No achievements are presented as earned.
            </p>
            <button
              type="button"
              className="continue-learning-button"
              onClick={() => navigate("/progress")}
            >
              View learning progress →
            </button>
          </div>
        </div>
      </section>

      {/* ================= EDIT PROFILE MODAL ================= */}

      {isEditing && (
        <div className="profile-modal-overlay">
          <div className="profile-modal">
            {/* Modal Header */}

            <div className="profile-modal-header">
              <h2>Edit Profile</h2>

              <button className="close-modal" onClick={handleCancel}>
                ✕
              </button>
            </div>

            {/* Profile Photo */}

            <div className="edit-photo-row">
              <div className="edit-photo">👤</div>

              <button
                className="change-photo-button"
                onClick={() => alert("Photo upload can be connected here.")}
              >
                Change
              </button>
            </div>

            {/* Full Name */}

            <div className="edit-field">
              <label>Full Name</label>

              <input
                type="text"
                name="name"
                value={editProfile.name}
                onChange={handleChange}
              />
            </div>

            {/* Email */}

            <div className="edit-field">
              <label>Email</label>

              <input
                type="email"
                name="email"
                value={editProfile.email}
                onChange={handleChange}
              />
            </div>

            {/* Phone */}

            <div className="edit-field">
              <label>Phone</label>

              <input
                type="text"
                name="phone"
                value={editProfile.phone}
                onChange={handleChange}
              />
            </div>

            {/* Department */}

            <div className="edit-field">
              <label>Department</label>

              <select
                name="department"
                value={editProfile.department}
                onChange={handleChange}
              >
                <option>Not configured</option>
                <option>Operations</option>
                <option>Finance</option>
                <option>Human Resources</option>
                <option>Information Technology</option>
                <option>Compliance</option>
              </select>
            </div>

            {/* Designation */}

            <div className="edit-field">
              <label>Designation</label>

              <input
                type="text"
                name="designation"
                value={editProfile.designation}
                onChange={handleChange}
              />
            </div>

            {/* Modal Buttons */}

            <div className="profile-modal-actions">
              <button className="modal-cancel-button" onClick={handleCancel}>
                Cancel
              </button>

              <button className="modal-save-button" onClick={handleSave}>
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Profile;
