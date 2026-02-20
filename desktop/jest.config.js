export default {
    preset: 'ts-jest',
    testEnvironment: 'jsdom',
    moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx'],
    setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
    transform: {
        '^.+\\.(ts|tsx)$': 'ts-jest',
    },
    moduleNameMapper: {
        '\\.(css|less|scss|sass)$': '<rootDir>/tests/__mocks__/styleMock.js',
        '^@/(.*)$': '<rootDir>/src/$1',
        '^.*/config/api$': '<rootDir>/tests/__mocks__/config/api.ts',
    },
    testMatch: [
        '<rootDir>/tests/**/*.test.(ts|tsx)',
    ],
};
