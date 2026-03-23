import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { EducationSection } from '../src/pages/ResumeManager/ResumeSections/EducationSection';
import { HeaderSection } from '../src/pages/ResumeManager/ResumeSections/HeaderSection';
import { SkillsSection } from '../src/pages/ResumeManager/ResumeSections/SkillsSection';
import { ProjectsSection } from '../src/pages/ResumeManager/ResumeSections/ProjectSections';
import { WorkExperienceSection } from '../src/pages/ResumeManager/ResumeSections/WorkExperienceSection';
import { AwardsSection } from '../src/pages/ResumeManager/ResumeSections/AwardsSection';
import { describe, test, expect } from '@jest/globals';
import '@testing-library/jest-dom';
import type { Education, Skills, Project, Resume, WorkExperience, Award } from '../src/api/resume_types';

describe('EducationSection', () => {
  test('renders education with all fields', () => {
    const education: Education[] = [{
      school: 'University of Example',
      degree: 'Bachelor of Science in Computer Science',
      dates: 'Sept 2020 – May 2024',
      gpa: '3.8'
    }];

    render(<EducationSection education={education} />);

    expect(screen.getByText('Education')).toBeDefined();
    expect(screen.getByText('University of Example')).toBeDefined();
    expect(screen.getByText('Bachelor of Science in Computer Science')).toBeDefined();
    expect(screen.getByText('Sept 2020 – May 2024')).toBeDefined();
    expect(screen.getByText(/GPA:.*3\.8/)).toBeDefined();
  });

  test('renders education with minimal fields', () => {
    const education: Education[] = [{
      school: 'Test University',
      degree: 'Computer Science',
      dates: '',
      gpa: ''
    }];

    render(<EducationSection education={education} />);

    expect(screen.getByText('Test University')).toBeDefined();
    expect(screen.getByText('Computer Science')).toBeDefined();
    expect(screen.queryByText(/GPA/)).toBeNull();
  });

  test('renders multiple education entries', () => {
    const education: Education[] = [
      {
        school: 'University A',
        degree: 'MSc Computer Science',
        dates: '2022 – 2024',
        gpa: '4.0'
      },
      {
        school: 'College B',
        degree: 'BSc Mathematics',
        dates: '2018 – 2022',
        gpa: '3.7'
      }
    ];

    render(<EducationSection education={education} />);

    expect(screen.getByText('University A')).toBeDefined();
    expect(screen.getByText('MSc Computer Science')).toBeDefined();
    expect(screen.getByText(/GPA:.*4\.0/)).toBeDefined();
    expect(screen.getByText('College B')).toBeDefined();
    expect(screen.getByText('BSc Mathematics')).toBeDefined();
    expect(screen.getByText(/GPA:.*3\.7/)).toBeDefined();
  });

  test('renders nothing when education array is empty', () => {
    const education: Education[] = [];

    const { container } = render(<EducationSection education={education} />);

    // Component renders the section header even when empty
    expect(screen.getByText('Education')).toBeDefined();
    // But no education entries should be present
    expect(container.querySelectorAll('.resume-preview__education-entry')).toHaveLength(0);
  });
});

describe('HeaderSection', () => {
  test('renders header with name and email', () => {
    const resume: Resume = {
      name: 'John Doe',
      email: 'john.doe@example.com',
      links: [],
      education: [],
      skills: { Proficient: [], Familiar: [] },
      projects: []
    };

    render(<HeaderSection resume={resume} />);

    expect(screen.getByText('John Doe')).toBeDefined();
    expect(screen.getByText('john.doe@example.com')).toBeDefined();
  });

  test('renders header with links', () => {
    const resume: Resume = {
      name: 'Jane Smith',
      email: 'jane@example.com',
      links: [
        { label: 'GitHub', url: 'https://github.com/janesmith' },
        { label: 'LinkedIn', url: 'https://linkedin.com/in/janesmith' }
      ],
      education: [],
      skills: { Proficient: [], Familiar: [] },
      projects: []
    };

    render(<HeaderSection resume={resume} />);

    expect(screen.getByText('Jane Smith')).toBeDefined();
    expect(screen.getByText('GitHub')).toBeDefined();
    expect(screen.getByText('LinkedIn')).toBeDefined();
    
    const githubLink = screen.getByText('GitHub').closest('a');
    expect(githubLink?.getAttribute('href')).toBe('https://github.com/janesmith');
  });

  test('renders header without links when array is empty', () => {
    const resume: Resume = {
      name: 'Test User',
      email: 'test@example.com',
      links: [],
      education: [],
      skills: { Proficient: [], Familiar: [] },
      projects: []
    };

    const { container } = render(<HeaderSection resume={resume} />);

    expect(screen.getByText('Test User')).toBeDefined();
    const linksSection = container.querySelector('.resume-preview__links');
    expect(linksSection).toBeNull();
  });

  test('email link has correct mailto href', () => {
    const resume: Resume = {
      name: 'Test User',
      email: 'test@example.com',
      links: [],
      education: [],
      skills: { Proficient: [], Familiar: [] },
      projects: []
    };

    render(<HeaderSection resume={resume} />);

    const emailLink = screen.getByText('test@example.com').closest('a');
    expect(emailLink?.getAttribute('href')).toBe('mailto:test@example.com');
  });
});

describe('SkillsSection', () => {
  test('renders skills list', () => {
    const skills: Skills = {
      Proficient: ['Python', 'JavaScript', 'React', 'Node.js', 'SQL'],
      Familiar: [],
    };

    render(<SkillsSection skills={skills} />);

    expect(screen.getByText('Skills')).toBeDefined();
    expect(screen.getByText('Python')).toBeDefined();
    expect(screen.getByText('JavaScript')).toBeDefined();
    expect(screen.getByText('React')).toBeDefined();
    expect(screen.getByText('Node.js')).toBeDefined();
    expect(screen.getByText('SQL')).toBeDefined();
  });

  test('renders empty skills list', () => {
    const skills: Skills = {
      Proficient: [],
      Familiar: []
    };

    const { container } = render(<SkillsSection skills={skills} />);

    expect(screen.getByText('Skills')).toBeDefined();
    const skillsList = container.querySelector('.resume-preview__skills-list');
    expect(skillsList?.textContent).toBe('');
  });
});

describe('ProjectsSection', () => {
  test('renders project with all fields', () => {
    const projects: Project[] = [
      {
        title: 'E-commerce Website',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['React', 'Node.js', 'MongoDB'],
        bullets: [
          'Built full-stack web application',
          'Implemented payment processing',
          'Deployed to AWS'
        ]
      }
    ];

    render(<ProjectsSection projects={projects} />);

    expect(screen.getByText('Projects / Experience')).toBeDefined();
    expect(screen.getByText('E-commerce Website')).toBeDefined();
    expect(screen.getByText('Jan 2024 – Mar 2024')).toBeDefined();
    expect(screen.getByText('React')).toBeDefined();
    expect(screen.getByText('Node.js')).toBeDefined();
    expect(screen.getByText('MongoDB')).toBeDefined();
    expect(screen.getByText('Built full-stack web application')).toBeDefined();
    expect(screen.getByText('Implemented payment processing')).toBeDefined();
    expect(screen.getByText('Deployed to AWS')).toBeDefined();
  });

  test('renders multiple projects', () => {
    const projects: Project[] = [
      {
        title: 'Project Alpha',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python', 'Flask'],
        bullets: ['Created REST API']
      },
      {
        title: 'Project Beta',
        dates: 'Apr 2024 – Jun 2024',
        skills: ['JavaScript', 'React'],
        bullets: ['Built dashboard UI']
      }
    ];

    render(<ProjectsSection projects={projects} />);

    expect(screen.getByText('Project Alpha')).toBeDefined();
    expect(screen.getByText('Project Beta')).toBeDefined();
    expect(screen.getByText('Python')).toBeDefined();
    expect(screen.getByText('JavaScript')).toBeDefined();
  });

  test('handles skills as comma-separated string', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024',
        skills: 'Python, Docker, Git' as unknown as string[], // Backend may return string
        bullets: ['Did something']
      }
    ];

    render(<ProjectsSection projects={projects} />);

    expect(screen.getByText('Python')).toBeDefined();
    expect(screen.getByText('Docker')).toBeDefined();
    expect(screen.getByText('Git')).toBeDefined();
  });

  test('handles missing bullets gracefully', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024',
        skills: ['Python'],
        bullets: []
      }
    ];

    const { container } = render(<ProjectsSection projects={projects} />);

    expect(screen.getByText('Test Project')).toBeDefined();
    const bulletList = container.querySelector('.resume-preview__project-bullets');
    expect(bulletList?.children.length).toBe(0);
  });

  test('hides heading when showHeading is false', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024',
        skills: ['Python'],
        bullets: ['Test bullet']
      }
    ];

    render(<ProjectsSection projects={projects} showHeading={false} />);

    expect(screen.queryByText('Projects / Experience')).toBeNull();
    expect(screen.getByText('Test Project')).toBeDefined();
  });

  test('renders empty projects list', () => {
    const projects: Project[] = [];

    const { container } = render(<ProjectsSection projects={projects} />);

    expect(screen.getByText('Projects / Experience')).toBeDefined();
    expect(container.querySelector('.resume-preview__project')).toBeNull();
  });

  test('skills are comma-separated in project', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024',
        skills: ['A', 'B', 'C'],
        bullets: []
      }
    ];

    const { container } = render(<ProjectsSection projects={projects} />);
    
    const skillsText = container.querySelector('.resume-preview__project-skills')?.textContent;
    expect(skillsText).toContain('A, B, C');
  });

  test('in edit mode shows month date inputs with Start/End placeholders', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet']
      }
    ];

    render(
      <ProjectsSection
        projects={projects}
        isEditing={true}
        onProjectChange={jest.fn()}
        projectStartIndex={0}
      />
    );

    expect(screen.getByLabelText('Start (month and year)')).toBeDefined();
    expect(screen.getByLabelText('End (month and year)')).toBeDefined();
    expect(screen.getByText('One bullet per line.')).toBeDefined();
  });

  test('in edit mode with onProjectDelete and project_id shows remove button', () => {
    const projects: Project[] = [
      {
        project_id: 'proj-123',
        title: 'Test Project',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet']
      }
    ];
    const onProjectDelete = jest.fn();

    render(
      <ProjectsSection
        projects={projects}
        isEditing={true}
        onProjectChange={jest.fn()}
        onProjectDelete={onProjectDelete}
        projectStartIndex={0}
      />
    );

    const removeButton = screen.getByRole('button', { name: 'Remove project from resume' });
    expect(removeButton).toBeDefined();
    expect(removeButton.textContent).toBe('×');
  });

  test('clicking remove project calls onProjectDelete after confirm', () => {
    const projects: Project[] = [
      {
        project_id: 'proj-456',
        title: 'Test Project',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet']
      }
    ];
    const onProjectDelete = jest.fn();
    window.confirm = jest.fn(() => true);

    render(
      <ProjectsSection
        projects={projects}
        isEditing={true}
        onProjectChange={jest.fn()}
        onProjectDelete={onProjectDelete}
        projectStartIndex={0}
      />
    );

    const removeButton = screen.getByRole('button', { name: 'Remove project from resume' });
    fireEvent.click(removeButton);

    expect(window.confirm).toHaveBeenCalledWith('Remove this project from the resume?');
    expect(onProjectDelete).toHaveBeenCalledWith('proj-456');
  });

  test('clicking remove project does not call onProjectDelete when user cancels confirm', () => {
    const projects: Project[] = [
      {
        project_id: 'proj-789',
        title: 'Test Project',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet']
      }
    ];
    const onProjectDelete = jest.fn();
    window.confirm = jest.fn(() => false);

    render(
      <ProjectsSection
        projects={projects}
        isEditing={true}
        onProjectChange={jest.fn()}
        onProjectDelete={onProjectDelete}
        projectStartIndex={0}
      />
    );

    const removeButton = screen.getByRole('button', { name: 'Remove project from resume' });
    fireEvent.click(removeButton);

    expect(window.confirm).toHaveBeenCalledWith('Remove this project from the resume?');
    expect(onProjectDelete).not.toHaveBeenCalled();
  });

  test('in edit mode without project_id does not show remove button', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet']
      }
    ];
    const onProjectDelete = jest.fn();

    render(
      <ProjectsSection
        projects={projects}
        isEditing={true}
        onProjectChange={jest.fn()}
        onProjectDelete={onProjectDelete}
        projectStartIndex={0}
      />
    );

    expect(screen.queryByRole('button', { name: 'Remove project from resume' })).toBeNull();
  });

  test('in edit mode with enableSortable shows drag handle per project', () => {
    const projects: Project[] = [
      {
        title: 'Project A',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet A']
      },
      {
        title: 'Project B',
        dates: 'Apr 2024 – Jun 2024',
        skills: ['JavaScript'],
        bullets: ['Bullet B']
      }
    ];

    render(
      <ProjectsSection
        projects={projects}
        isEditing={true}
        onProjectChange={jest.fn()}
        projectStartIndex={0}
        enableSortable={true}
      />
    );

    const dragHandles = screen.getAllByLabelText('Drag to reorder project');
    expect(dragHandles.length).toBe(2);
  });

  test('in edit mode without enableSortable does not show drag handle', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet']
      }
    ];

    render(
      <ProjectsSection
        projects={projects}
        isEditing={true}
        onProjectChange={jest.fn()}
        projectStartIndex={0}
      />
    );

    expect(screen.queryByLabelText('Drag to reorder project')).toBeNull();
  });

  test('when not editing enableSortable does not show drag handle', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet']
      }
    ];

    render(
      <ProjectsSection
        projects={projects}
        enableSortable={true}
        projectStartIndex={0}
      />
    );

    expect(screen.queryByLabelText('Drag to reorder project')).toBeNull();
  });

  test('in edit mode with onAddProjectClick shows Add a project button', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet']
      }
    ];
    const onAddProjectClick = jest.fn();

    render(
      <ProjectsSection
        projects={projects}
        showHeading={true}
        isEditing={true}
        onProjectChange={jest.fn()}
        onAddProjectClick={onAddProjectClick}
        projectStartIndex={0}
      />
    );

    const addButton = screen.getByRole('button', { name: 'Add a project' });
    expect(addButton).toBeDefined();
    fireEvent.click(addButton);
    expect(onAddProjectClick).toHaveBeenCalledTimes(1);
  });

  test('in edit mode without onAddProjectClick does not show Add a project button', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet']
      }
    ];

    render(
      <ProjectsSection
        projects={projects}
        showHeading={true}
        isEditing={true}
        onProjectChange={jest.fn()}
        projectStartIndex={0}
      />
    );

    expect(screen.queryByRole('button', { name: 'Add a project' })).toBeNull();
  });

  test('when showHeading is false does not show Add a project button even with onAddProjectClick', () => {
    const projects: Project[] = [
      {
        title: 'Test Project',
        dates: 'Jan 2024 – Mar 2024',
        skills: ['Python'],
        bullets: ['Bullet']
      }
    ];
    const onAddProjectClick = jest.fn();

    render(
      <ProjectsSection
        projects={projects}
        showHeading={false}
        isEditing={true}
        onProjectChange={jest.fn()}
        onAddProjectClick={onAddProjectClick}
        projectStartIndex={0}
      />
    );

    expect(screen.queryByRole('button', { name: 'Add a project' })).toBeNull();
  });
});

describe('WorkExperienceSection', () => {
  test('renders work experience with company, role, date, and details', () => {
    const workExperience: WorkExperience[] = [
      {
        role: 'Software Engineer',
        company: 'Tech Corp',
        start_date: '2024-01',
        end_date: '2024-06',
        details: ['Built APIs', 'Led team meetings']
      }
    ];

    render(<WorkExperienceSection workExperience={workExperience} />);

    expect(screen.getByText('Work Experience')).toBeDefined();
    expect(screen.getByText('Tech Corp | Software Engineer')).toBeDefined();
    expect(screen.getByText('Jan 2024 – Jun 2024')).toBeDefined();
    expect(screen.getByText('Built APIs')).toBeDefined();
    expect(screen.getByText('Led team meetings')).toBeDefined();
  });

  test('renders work experience with role only when no company', () => {
    const workExperience: WorkExperience[] = [
      { role: 'Intern', start_date: '2023-06', end_date: '2023-08', details: [] }
    ];

    render(<WorkExperienceSection workExperience={workExperience} />);

    expect(screen.getByText('Intern')).toBeDefined();
    expect(screen.getByText('Jun 2023 – Aug 2023')).toBeDefined();
  });

  test('renders empty state when no entries', () => {
    render(<WorkExperienceSection workExperience={[]} />);

    expect(screen.getByText('Work Experience')).toBeDefined();
    expect(screen.getByText('No work experience added.')).toBeDefined();
  });

  test('in edit mode shows Add a role button', () => {
    const onChange = jest.fn();
    render(<WorkExperienceSection workExperience={[]} isEditing={true} onChange={onChange} />);

    const addButton = screen.getByRole('button', { name: 'Add a role' });
    expect(addButton).toBeDefined();
    fireEvent.click(addButton);
    expect(onChange).toHaveBeenCalledWith([
      { role: '', company: '', start_date: '', end_date: '', details: [] }
    ]);
  });

  test('in edit mode shows company, role, date inputs and responsibilities textarea', () => {
    const workExperience: WorkExperience[] = [
      { role: 'Developer', company: 'Acme', start_date: '2024-01', end_date: '2024-06', details: ['Task 1'] }
    ];

    render(<WorkExperienceSection workExperience={workExperience} isEditing={true} onChange={jest.fn()} />);

    expect(screen.getByPlaceholderText('Company / organization')).toHaveValue('Acme');
    expect(screen.getByPlaceholderText('Role title (required)')).toHaveValue('Developer');
    expect(screen.getByLabelText('Start (month and year)')).toHaveValue('2024-01');
    expect(screen.getByLabelText('End (month and year)')).toHaveValue('2024-06');
    expect(screen.getByPlaceholderText(/Responsibility one/)).toBeDefined();
    expect(screen.getByText('One bullet per line.')).toBeDefined();
  });

  test('in edit mode remove button calls onChange with entry removed', () => {
    const workExperience: WorkExperience[] = [
      { role: 'Dev', company: 'Co', start_date: '2024-01', end_date: '2024-06', details: [] }
    ];
    const onChange = jest.fn();

    render(<WorkExperienceSection workExperience={workExperience} isEditing={true} onChange={onChange} />);

    const removeBtn = screen.getByRole('button', { name: 'Remove work experience entry' });
    fireEvent.click(removeBtn);
    expect(onChange).toHaveBeenCalledWith([]);
  });

  test('in edit mode with enableSortable shows drag handle per entry', () => {
    const workExperience: WorkExperience[] = [
      { role: 'A', company: 'Co1', start_date: '', end_date: '', details: [] },
      { role: 'B', company: 'Co2', start_date: '', end_date: '', details: [] },
    ];

    render(
      <WorkExperienceSection
        workExperience={workExperience}
        isEditing={true}
        onChange={jest.fn()}
        enableSortable={true}
      />,
    );

    const dragHandles = screen.getAllByLabelText('Drag to reorder work experience');
    expect(dragHandles.length).toBe(2);
  });

  test('in edit mode without enableSortable does not show work experience drag handle', () => {
    const workExperience: WorkExperience[] = [
      { role: 'A', company: 'Co', start_date: '', end_date: '', details: [] },
    ];

    render(
      <WorkExperienceSection workExperience={workExperience} isEditing={true} onChange={jest.fn()} />,
    );

    expect(screen.queryByLabelText('Drag to reorder work experience')).toBeNull();
  });

  test('in edit mode updating company calls onChange', async () => {
    const workExperience: WorkExperience[] = [
      { role: 'Dev', company: '', start_date: '', end_date: '', details: [] }
    ];
    const onChange = jest.fn();

    render(<WorkExperienceSection workExperience={workExperience} isEditing={true} onChange={onChange} />);

    const companyInput = screen.getByPlaceholderText('Company / organization');
    await userEvent.type(companyInput, 'NewCo');
    expect(onChange).toHaveBeenCalled();
  });
});

describe('AwardsSection', () => {
  test('renders award with title, issuer, date, and details', () => {
    const awards: Award[] = [
      {
        title: 'Hackathon Winner',
        issuer: 'Tech Challenge Inc.',
        date: '2024-03',
        details: ['Won first place', 'Built AI assistant']
      }
    ];

    render(<AwardsSection awards={awards} />);

    expect(screen.getByText('Awards & Honours')).toBeDefined();
    expect(screen.getByText('Hackathon Winner')).toBeDefined();
    expect(screen.getByText('Tech Challenge Inc.')).toBeDefined();
    expect(screen.getByText('Mar 2024')).toBeDefined();
    expect(screen.getByText('Won first place')).toBeDefined();
    expect(screen.getByText('Built AI assistant')).toBeDefined();
  });

  test('renders award with minimal fields', () => {
    const awards: Award[] = [{ title: 'Employee of the Month' }];

    render(<AwardsSection awards={awards} />);

    expect(screen.getByText('Employee of the Month')).toBeDefined();
  });

  test('renders empty state when no awards and not editing', () => {
    render(<AwardsSection awards={[]} />);

    expect(screen.getByText('Awards & Honours')).toBeDefined();
    expect(screen.getByText('No awards added.')).toBeDefined();
  });

  test('in edit mode shows Add an award button', () => {
    const onChange = jest.fn();
    render(<AwardsSection awards={[]} isEditing={true} onChange={onChange} />);

    expect(screen.getByText('Add your awards & honours below.')).toBeDefined();
    const addButton = screen.getByRole('button', { name: 'Add an award' });
    expect(addButton).toBeDefined();
    fireEvent.click(addButton);
    expect(onChange).toHaveBeenCalledWith([
      { title: '', issuer: '', date: '', details: [] }
    ]);
  });

  test('in edit mode shows title, issuer, date inputs and details textarea', () => {
    const awards: Award[] = [
      { title: 'Best Paper', issuer: 'ACM', date: '2024-01', details: ['Peer reviewed'] }
    ];

    render(<AwardsSection awards={awards} isEditing={true} onChange={jest.fn()} />);

    expect(screen.getByPlaceholderText('Award title (required)')).toHaveValue('Best Paper');
    expect(screen.getByPlaceholderText('Issuer / organization')).toHaveValue('ACM');
    expect(screen.getByLabelText('Award date (month-year)')).toHaveValue('2024-01');
    expect(screen.getByPlaceholderText('Award details (one per line)')).toBeDefined();
  });

  test('in edit mode remove button calls onChange with award removed', () => {
    const awards: Award[] = [
      { title: 'Award', issuer: 'Org', date: '2024-01', details: [] }
    ];
    const onChange = jest.fn();

    render(<AwardsSection awards={awards} isEditing={true} onChange={onChange} />);

    const removeBtn = screen.getByRole('button', { name: 'Remove award' });
    fireEvent.click(removeBtn);
    expect(onChange).toHaveBeenCalledWith([]);
  });

  test('in edit mode with enableSortable shows drag handle per award', () => {
    const awards: Award[] = [
      { title: 'One', issuer: '', date: '', details: [] },
      { title: 'Two', issuer: '', date: '', details: [] },
    ];

    render(
      <AwardsSection awards={awards} isEditing={true} onChange={jest.fn()} enableSortable={true} />,
    );

    const dragHandles = screen.getAllByLabelText('Drag to reorder award');
    expect(dragHandles.length).toBe(2);
  });

  test('in edit mode without enableSortable does not show award drag handle', () => {
    const awards: Award[] = [{ title: 'One', issuer: '', date: '', details: [] }];

    render(<AwardsSection awards={awards} isEditing={true} onChange={jest.fn()} />);

    expect(screen.queryByLabelText('Drag to reorder award')).toBeNull();
  });
});
