import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Profile.css";

function Profile() {
  const navigate = useNavigate();

  const [isEditing, setIsEditing] = useState(false);

  const [profile, setProfile] = useState({
    name: "Employee Name",
    designation: "Senior Officer",
    department: "Operations",
    employeeId: "RBI000123",
    email: "employee@example.com",
    phone: "+91 XXXXX XXXXX",
    branch: "Mumbai",
    joiningDate: "10 June 2024",
  });

  const [editProfile, setEditProfile] = useState(profile);

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

        <p>Manage your employee information and learning profile</p>
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

        <div className="learning-summary-card">
          <div className="learning-summary-stats">
            <div className="learning-stat">
              <span>Courses Completed</span>
              <strong>12</strong>
            </div>

            <div className="learning-stat">
              <span>Learning Hours</span>
              <strong>18h</strong>
            </div>

            <div className="learning-stat">
              <span>Assessments Average</span>
              <strong>82%</strong>
            </div>

            <div className="learning-stat">
              <span>Certificates</span>
              <strong>5</strong>
            </div>
          </div>

          {/* Current Learning */}

          <div className="current-learning">
            <h3>Current Learning</h3>

            <div className="current-learning-name">Regulatory Compliance</div>

            <div className="learning-progress-wrapper">
              <div className="learning-progress-bar">
                <div
                  className="learning-progress-fill"
                  style={{ width: "85%" }}
                ></div>
              </div>

              <span>85%</span>
            </div>

            <button
              className="continue-learning-button"
              onClick={() => navigate("/learning")}
            >
              Continue Learning →
            </button>
          </div>
        </div>
      </section>

      {/* ================= ACHIEVEMENTS ================= */}

      <section className="profile-section">
        <h2>🏆 Achievements</h2>

        <div className="achievement-grid">
          {/* Compliance */}

          <div className="profile-achievement-card">
            <div className="profile-achievement-icon">🎓</div>

            <h3>Compliance</h3>

            <p>Certificate</p>

            <span>✓ Earned</span>
          </div>

          {/* Cyber Security */}

          <div className="profile-achievement-card">
            <div className="profile-achievement-icon">🏅</div>

            <h3>Cyber Security</h3>

            <p>Badge</p>

            <span>✓ Earned</span>
          </div>

          {/* Learning Streak */}

          <div className="profile-achievement-card">
            <div className="profile-achievement-icon">🔥</div>

            <h3>7 Day Learning</h3>

            <p>Streak</p>

            <span>✓ Achieved</span>
          </div>
        </div>

        <div className="view-achievements-wrapper">
          <button
            className="view-achievements-button"
            onClick={() => navigate("/performance")}
          >
            View All Achievements
          </button>
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
