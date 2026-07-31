package services

import (
	"testing"
)

func TestErrInsufficientBalance(t *testing.T) {
	err := ErrInsufficientBalance
	expected := "insufficient MTC balance"
	if err.Error() != expected {
		t.Errorf("Expected error message '%s', got '%s'", expected, err.Error())
	}
}

func TestErrInvalidAmount(t *testing.T) {
	err := ErrInvalidAmount
	expected := "invalid amount: must be positive"
	if err.Error() != expected {
		t.Errorf("Expected error message '%s', got '%s'", expected, err.Error())
	}
}

func TestErrSameAccount(t *testing.T) {
	err := ErrSameAccount
	expected := "cannot transfer to same account"
	if err.Error() != expected {
		t.Errorf("Expected error message '%s', got '%s'", expected, err.Error())
	}
}

func TestServiceError(t *testing.T) {
	customErr := &ServiceError{Message: "custom error message"}
	if customErr.Error() != "custom error message" {
		t.Errorf("Expected error message 'custom error message', got '%s'", customErr.Error())
	}
}
