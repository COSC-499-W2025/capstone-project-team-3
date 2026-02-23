import { render, screen } from '@testing-library/react';
import { EducationSection } from '../src/pages/ResumeManager/ResumeSections/EducationSection';
import { HeaderSection } from '../src/pages/ResumeManager/ResumeSections/HeaderSection';
import { SkillsSection } from '../src/pages/ResumeManager/ResumeSections/SkillsSection';
import { ProjectsSection } from '../src/pages/ResumeManager/ResumeSections/ProjectSections';
import { describe, test, expect } from '@jest/globals';
import '@testing-library/jest-dom';
import type { Education, Skills, Project, Resume } from '../src/api/resume_types';

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
      skills: { Skills: [] },
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
      skills: { Skills: [] },
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
      skills: { Skills: [] },
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
      skills: { Skills: [] },
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
      Skills: ['Python', 'JavaScript', 'React', 'Node.js', 'SQL']
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
      Skills: []
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
});
