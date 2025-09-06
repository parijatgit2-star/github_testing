import { useRouter } from 'next/router';
import React, { useState, useEffect } from 'react';

/**
 * Displays the detailed view for a single issue.
 *
 * Fetches the issue details and its associated comments from the backend API
 * based on the ID from the URL. Allows staff to update the issue's status
 * and assigned department.
 * @returns {React.ReactElement} The issue detail page component.
 */
export default function IssueDetailPage() {
  const router = useRouter();
  const { id } = router.query;

  const [issue, setIssue] = useState(null);
  const [comments, setComments] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [error, setError] = useState(null);

  // State for form inputs
  const [status, setStatus] = useState('');
  const [departmentId, setDepartmentId] = useState('');
  const [updateMessage, setUpdateMessage] = useState('');


  useEffect(() => {
    if (!id) return;

    async function fetchIssueDetails() {
      try {
        // Fetch main issue data
        const issueRes = await fetch(`http://localhost:8000/issues/${id}`);
        if (!issueRes.ok) throw new Error(`Failed to fetch issue ${id}`);
        const issueData = await issueRes.json();
        setIssue(issueData);
        setStatus(issueData.status);
        setDepartmentId(issueData.department_id || '');

        // Fetch comments
        const commentsRes = await fetch(`http://localhost:8000/issues/${id}/comments`);
        if (commentsRes.ok) setComments(await commentsRes.json());

        // Fetch departments for dropdown
        const deptsRes = await fetch(`http://localhost:8000/departments/`);
        if (deptsRes.ok) setDepartments(await deptsRes.json());

      } catch (err) {
        setError(err.message);
        console.error(err);
      }
    }

    fetchIssueDetails();
  }, [id]);

  const handleSaveChanges = async () => {
    setUpdateMessage('Saving...');
    try {
      const payload = {
        status: status,
        department_id: departmentId || null,
      };
      const res = await fetch(`http://localhost:8000/issues/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const errBody = await res.text();
        throw new Error(`Failed to update: ${errBody}`);
      }
      const updatedIssue = await res.json();
      setIssue(updatedIssue);
      setUpdateMessage('Changes saved successfully!');
    } catch (err) {
      setUpdateMessage(`Error: ${err.message}`);
    }
  };

  if (error) return <div style={{ padding: 24 }}><p style={{ color: 'red' }}>Error: {error}</p></div>;
  if (!issue) return <div style={{ padding: 24 }}><p>Loading...</p></div>;

  return (
    <div style={{ padding: 24 }}>
      <h1>{issue.title}</h1>
      <p><strong>Category:</strong> {issue.category || 'N/A'}</p>
      <p><strong>Reported:</strong> {new Date(issue.created_at).toLocaleString()}</p>

      <div style={{ margin: '16px 0', borderTop: '1px solid #eee', paddingTop: 16 }}>
        <h2>Staff Actions</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 300 }}>
          <div>
            <label htmlFor="status-select">Status</label>
            <select id="status-select" value={status} onChange={e => setStatus(e.target.value)} style={{ width: '100%', padding: 8 }}>
              <option value="pending">Pending</option>
              <option value="assigned">Assigned</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div>
            <label htmlFor="dept-select">Department</label>
            <select id="dept-select" value={departmentId} onChange={e => setDepartmentId(e.target.value)} style={{ width: '100%', padding: 8 }}>
              <option value="">-- Unassigned --</option>
              {departments.map(dept => (
                <option key={dept.id} value={dept.id}>{dept.name}</option>
              ))}
            </select>
          </div>
          <button onClick={handleSaveChanges} style={{ padding: 10, background: '#3b82f6', color: 'white', border: 'none', borderRadius: 4 }}>Save Changes</button>
          {updateMessage && <p>{updateMessage}</p>}
        </div>
      </div>

      <div style={{ margin: '16px 0', borderTop: '1px solid #eee', paddingTop: 16 }}>
        <h2>Description</h2>
        <p>{issue.description}</p>
      </div>

      {issue.images && issue.images.length > 0 && (
        <div style={{ margin: '16px 0' }}>
          <h2>Photos</h2>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
            {issue.images.map(img => (
              <img key={img.public_id || img.url} src={img.url} alt="Issue image" style={{ width: 200, height: 200, objectFit: 'cover' }} />
            ))}
          </div>
        </div>
      )}

      <div style={{ margin: '16px 0', borderTop: '1px solid #eee', paddingTop: 16 }}>
        <h2>Comments</h2>
        {comments.length > 0 ? (
          <ul>
            {comments.map(comment => (
              <li key={comment.id} style={{ marginBottom: 8 }}>
                <p>{comment.text}</p>
                <small>By: {comment.user_id || 'Anonymous'} on {new Date(comment.created_at).toLocaleDateString()}</small>
              </li>
            ))}
          </ul>
        ) : (
          <p>No comments yet.</p>
        )}
      </div>
    </div>
  );
}
