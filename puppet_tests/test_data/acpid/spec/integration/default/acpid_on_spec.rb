require File.expand_path('../../spec_helper', __FILE__)

describe package('acpid') do
  it { should be_installed }
end

describe service('acpid') do
  it { should be_enabled }
  it { should be_running }
end
