/**
 * JS wrapper around window.pywebview.api.
 * All methods unwrap {ok, data} and throw on error.
 */

async function call(method, ...args) {
  if (!window.pywebview || !window.pywebview.api) {
    throw new Error(`pywebview.api not ready (calling ${method})`);
  }
  const result = await window.pywebview.api[method](...args);
  if (!result.ok) throw new Error(result.error || 'Unknown error');
  return result.data;
}

export const api = {
  // Presets
  getPresets:   ()                   => call('get_presets'),
  loadPreset:   (path)               => call('load_preset', path),
  newPreset:    (name)               => call('new_preset', name),
  savePreset:   (name, steps)        => call('save_preset', name, steps),
  deletePreset: (path)               => call('delete_preset', path),
  exportPreset: (path)               => call('export_preset', path),

  // File
  openFileDialog:   ()               => call('open_file_dialog'),
  clearFile:        ()               => call('clear_file'),
  getSourceColumns: ()               => call('get_source_columns'),

  // Steps
  getStepPayload: (action)           => call('get_step_payload', action),
  setStepPayload: (action, payload)  => call('set_step_payload', action, payload),
};
