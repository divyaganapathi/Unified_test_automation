/**
 * Structured Logger Utility
 * Provides consistent, timestamped logging across the framework
 */

type LogLevel = 'INFO' | 'ERROR' | 'WARN' | 'DEBUG';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  context?: string;
  message: string;
  data?: any;
}

class Logger {
  private formatTimestamp(): string {
    return new Date().toISOString();
  }

  private formatLog(entry: LogEntry): string {
    const { timestamp, level, context, message, data } = entry;
    const contextStr = context ? `[${context}]` : '';
    const dataStr = data ? ` | ${JSON.stringify(data)}` : '';
    return `${timestamp} [${level}] ${contextStr} ${message}${dataStr}`;
  }

  private log(level: LogLevel, message: string, context?: string, data?: any): void {
    const entry: LogEntry = { timestamp: this.formatTimestamp(), level, context, message, data };
    const formatted = this.formatLog(entry);

    if (level === 'ERROR') {
      console.error(formatted);
    } else if (level === 'WARN') {
      console.warn(formatted);
    } else {
      console.log(formatted);
    }
  }

  info(message: string, context?: string, data?: any): void {
    this.log('INFO', message, context, data);
  }

  error(message: string, context?: string, error?: any): void {
    this.log('ERROR', message, context, error);
  }

  warn(message: string, context?: string, data?: any): void {
    this.log('WARN', message, context, data);
  }

  debug(message: string, context?: string, data?: any): void {
    // Only log debug if DEBUG env var is set
    if (process.env.DEBUG === 'true') {
      this.log('DEBUG', message, context, data);
    }
  }

  stepStart(stepName: string): void {
    this.info(`→ ${stepName}`, 'STEP');
  }

  stepEnd(stepName: string): void {
    this.info(`✓ ${stepName}`, 'STEP');
  }

  apiCall(method: string, endpoint: string, status?: number): void {
    const statusStr = status ? ` | Status: ${status}` : '';
    this.info(`API ${method} ${endpoint}${statusStr}`, 'API');
  }

  assertion(description: string, passed: boolean): void {
    const symbol = passed ? '✓' : '✗';
    this.info(`${symbol} Assertion: ${description}`, 'ASSERT', { passed });
  }
}

export const logger = new Logger();
