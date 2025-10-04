import { OpenRouterAgent } from './OpenRouterAgent';

export class EventGenerator extends OpenRouterAgent {
    constructor(apiKey?: string, model?: string) {
        super(apiKey, model || 'openai/gpt-3.5-turbo', 1500, 0.8);
    }

    protected getSystemPrompt(): string {
        return ``; //TODO: uzupełnij
    }

    public async process(input: string, context?: any): Promise<string> {
        try {
            const prompt = context?.additionalContext
                ? `${input}\n\nAdditional context: ${context.additionalContext}`
                : input;

            const response = await this.sendMessage(prompt);
            return response;
        } catch (error) {
            throw new Error(`EventGenerator processing failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }

    /**
     * Generate a specific type of event
     */
    public async generateEvent(
        eventType: string,
        audience: string,
        duration: string,
        constraints?: string
    ): Promise<string> {
        const prompt = `Generate a detailed ${eventType} event for ${audience} lasting ${duration}.${constraints ? ` Constraints: ${constraints}` : ''
            }`;

        return this.process(prompt);
    }
}
