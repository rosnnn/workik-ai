import * as vscode from 'vscode';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
	console.log('✅ Workik AI Agent extension is now active!');

	const disposable = vscode.commands.registerCommand('workik-ai-agent.runAgent', () => {
		const extensionPath = context.extensionPath;
		const scriptPath = path.join(extensionPath, 'ai_agent.py');

		// Check Python path (optional: customize or detect)
		const pythonCmd = 'python'; // or provide full path like 'C:\\Python311\\python.exe'

		const terminal = vscode.window.createTerminal({
			name: 'Workik AI Agent',
			cwd: extensionPath,
			shellPath: pythonCmd,
			shellArgs: [scriptPath]
		});

		terminal.show();
	});

	context.subscriptions.push(disposable);
}

export function deactivate() {}
