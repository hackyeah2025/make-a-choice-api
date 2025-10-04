import { OpenRouterAgent } from './OpenRouterAgent';

export class Summarizer extends OpenRouterAgent {
    constructor(apiKey?: string, model?: string) {
        super(apiKey, model || 'openai/gpt-3.5-turbo', 800, 0.3);
    }

    protected getSystemPrompt(): string {
        return ``; //TODO: uzupełnij
    }

    public async process(input: string, context?: any): Promise<string> {
        try {
            const summaryLength = context?.length || 'medium';
            const prompt = `Please summarize the following content with a ${summaryLength} length summary:\n\n${input}`;

            const response = await this.sendMessage(prompt);
            return response;
        } catch (error) {
            throw new Error(`Summarizer processing failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    /**
     * Summarize content with a specific length constraint
     */
    public async summarizeWithLength(
        content: string,
        maxWords: number,
        focusAreas?: string[]
    ): Promise<string> {
        const focusPrompt = focusAreas?.length
            ? `\nFocus on these areas: ${focusAreas.join(', ')}.`
            : '';

        const prompt = `Summarize the following content in ${maxWords} words or less.${focusPrompt}\n\n${content}`;
        return this.process(prompt);
    }

    /**
     * Create a bullet point summary
     */
    public async createBulletSummary(
        content: string,
        maxPoints: number = 5
    ): Promise<string> {
        const prompt = `Create a bullet point summary of the following content with no more than ${maxPoints} key points:\n\n${content}`;
        return this.process(prompt);
    }
}
