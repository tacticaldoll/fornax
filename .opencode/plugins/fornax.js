/**
 * Fornax plugin for OpenCode.ai
 *
 * Registers the Fornax skills directory so OpenCode discovers the skills, with
 * no symlinks required. Fornax does not inject a bootstrap message — skills load
 * on demand via OpenCode's native `skill` tool, not into every session.
 */

import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fornaxSkillsDir = path.resolve(__dirname, '../../skills');

export const FornaxPlugin = async () => ({
  // Inject the skills path into live config so OpenCode discovers Fornax skills
  // without manual symlinks or config edits.
  config: async (config) => {
    config.skills = config.skills || {};
    config.skills.paths = config.skills.paths || [];
    if (!config.skills.paths.includes(fornaxSkillsDir)) {
      config.skills.paths.push(fornaxSkillsDir);
    }
  },
});
