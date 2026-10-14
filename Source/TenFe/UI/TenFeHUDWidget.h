#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TenFeHUDWidget.generated.h"

class ATenFeCharacter;
class UProgressBar;
class UTextBlock;

UCLASS()
class TENFE_API UTenFeHUDWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    void SetCharacter(ATenFeCharacter* InCharacter);

protected:
    virtual void NativeConstruct() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
    void BuildLayout();
    void Refresh();

    UPROPERTY()
    TObjectPtr<ATenFeCharacter> Character;

    UPROPERTY()
    TObjectPtr<UProgressBar> HealthBar;

    UPROPERTY()
    TObjectPtr<UProgressBar> StaminaBar;

    UPROPERTY()
    TObjectPtr<UTextBlock> EquipmentText;
};
